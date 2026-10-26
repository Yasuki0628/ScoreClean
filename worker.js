// Cloudflare Worker (module syntax). Set OPENAI_API_KEY as a secret, not in source.
const PROMPT = `Read this Japanese baseball scorebook. Return a JSON object with meta, scores, players, diagrams, uncertain, observations. meta fields: tournament,date,venue,round,away,home,scorer. scores: away and home arrays of inning scores. players: away/home arrays of batting-order objects with name,position,number,plays (inning-index keys). diagrams: keys away:rowIndex:inningIndex or home:rowIndex:inningIndex with result,note,bases,out. observations: list of {bbox:[left,top,right,bottom],confidence,result,note,bases,out}; bbox is in image pixels and must be omitted if unknown. Do not invent entries or coordinates; ambiguous entries belong in uncertain. Use Japanese baseball scoring notation.`;
function json(data,status=200,origin='*'){return new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Access-Control-Allow-Origin':origin,'Vary':'Origin','Cache-Control':'no-store'}})}
function allowedOrigin(request,env){const origin=request.headers.get('Origin')||'';const configured=(env.ALLOWED_ORIGINS||'').split(',').map(x=>x.trim()).filter(Boolean);return configured.includes(origin)?origin:null}
export default {async fetch(request,env){
 const origin=allowedOrigin(request,env);const url=new URL(request.url);
 if(request.method==='OPTIONS'){return new Response(null,{status:204,headers:{'Access-Control-Allow-Origin':origin||'null','Access-Control-Allow-Methods':'POST,GET,OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'86400','Vary':'Origin'}})}
 if(!origin)return json({error:'このGitHub PagesのOriginは許可されていません。ALLOWED_ORIGINSを確認してください。'},403,'null');
 if(url.pathname==='/api/health'&&request.method==='GET')return json({ok:true,aiConfigured:!!env.OPENAI_API_KEY},200,origin);
 if(url.pathname==='/api/layout')return json({code:'LAYOUT_UNAVAILABLE',error:'クラウド版ではOpenCV罫線補正は未対応です。原画像でAI読取します。'},501,origin);
 if(url.pathname==='/api/map-cells')return json({error:'座標照合はクラウド版では未対応です。'},501,origin);
 if(url.pathname!=='/api/recognize'||request.method!=='POST')return json({error:'Not found'},404,origin);
 if(!env.OPENAI_API_KEY)return json({error:'Cloudflare WorkerのOPENAI_API_KEYが未設定です'},503,origin);
 try{
  const form=await request.formData();const file=form.get('image');if(!(file instanceof File)||!file.type.startsWith('image/'))return json({error:'画像ファイルを選択してください'},400,origin);
  if(file.size>8_000_000)return json({error:'画像は8MB以下にしてください'},413,origin);
  const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  const payload={model:env.OPENAI_MODEL||'gpt-4.1-mini',messages:[{role:'system',content:PROMPT},{role:'user',content:[{type:'text',text:'Transcribe the scorebook image into JSON. Return observed entries only.'},{type:'image_url',image_url:{url:`data:${file.type};base64,${btoa(binary)}`}}]}],response_format:{type:'json_object'},max_tokens:6000};
  const response=await fetch('https://api.openai.com/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${env.OPENAI_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const body=await response.json();if(!response.ok)return json({error:'OpenAI API error: '+(body.error?.message||response.status)},502,origin);
  const raw=body.choices?.[0]?.message?.content;if(!raw)return json({error:'AIの応答が空です'},502,origin);
  const result=JSON.parse(raw);if(!result.players||!result.scores)return json({error:'AI応答にplayers/scoresがありません'},502,origin);
  return json({result},200,origin);
 }catch(e){return json({error:'解析失敗: '+(e?.message||'unknown')},500,origin)}
}};
