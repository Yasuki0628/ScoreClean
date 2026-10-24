"""Optional local recognition proxy. Python 3.10+, no third-party packages."""
import os, json, base64, urllib.request, urllib.error, cgi
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT=Path(__file__).parent
PROMPT='''You are transcribing a Japanese baseball scorebook photo into a digital scorebook. Preserve the inning-by-inning cells, including each batting outcome, base-running notations, substitutions, and ambiguous markings. Return ONLY a JSON object with keys meta, scores, players, diagrams, uncertain. diagrams is an object keyed "away:rowIndex:inningIndex" or "home:rowIndex:inningIndex" (zero-based), each value {"result":"K", "note":"6-3", "bases":0, "out":"1"}. Only populate diagrams when confident; do not invent geometry. meta keys tournament,date,venue,round,away,home,scorer (strings, blank if unknown). scores keys away,home each array of up to 9 strings (blank for unreadable). players keys away,home each array in batting-order row order, each element {"name":"", "position":"", "number":"", "plays":{"0":"first inning marks", "1":"second inning marks"}}. Do not hallucinate. When uncertain, use 要確認 in the corresponding cell and describe exact uncertainty in uncertain string array. Preserve scorebook symbols as text, e.g. 三振K, 四球BB, 盗塁, 進塁, and describe where symbol location matters. Treat handwritten inning boundaries carefully. Only output observed entries. Additionally return observations array; each observation has bbox [left,top,right,bottom] in PIXELS of the submitted image, confidence 0..1, result, note, bases, out. Never fabricate coordinates; omit observation if bbox cannot be established.'''
class Handler(BaseHTTPRequestHandler):
 def send(self, code, obj):
  b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  path=self.path.split('?')[0]
  if path=='/':path='/index.html'
  file=(ROOT/path.lstrip('/')).resolve()
  if ROOT not in file.parents or not file.is_file():self.send_error(404);return
  typ={'.html':'text/html','.js':'application/javascript','.svg':'image/svg+xml','.webmanifest':'application/manifest+json'}.get(file.suffix,'application/octet-stream')
  b=file.read_bytes();self.send_response(200);self.send_header('Content-Type',typ+'; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_POST(self):
  if self.path not in ('/api/recognize','/api/layout','/api/map-cells'):self.send(404,{'error':'Not found'});return
  if self.path=='/api/map-cells':
   try:
    from cell_mapping import map_cells
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<2000000:raise ValueError('JSONサイズが不正')
    data=json.loads(self.rfile.read(n))
    self.send(200,map_cells(data['layout'],data.get('observations',[]),row_start=int(data.get('rowStart',0)),col_start=int(data.get('colStart',0)),rows=int(data.get('rows',9)),cols=int(data.get('cols',6)),side=data.get('side','away')))
   except Exception as e:self.send(400,{'error':str(e)})
   return
  if self.path=='/api/recognize' and not os.getenv('OPENAI_API_KEY'):self.send(503,{'error':'サーバーの OPENAI_API_KEY が未設定です'});return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=12_000_000:raise ValueError('画像は12MB以下にしてください')
   content=self.rfile.read(length)
   boundary=self.headers.get('Content-Type','').split('boundary=')[-1].encode()
   if not boundary or b'filename=' not in content:raise ValueError('画像がありません')
   chunks=content.split(b'--'+boundary)
   image=None;mime='image/jpeg'
   for chunk in chunks:
    if b'name="image"' in chunk:
     head,body=chunk.split(b'\r\n\r\n',1);image=body.rsplit(b'\r\n',1)[0]
     if b'image/png' in head:mime='image/png'
     elif b'image/webp' in head:mime='image/webp'
     break
   if not image or len(image)>10_000_000:raise ValueError('有効な10MB以下の画像を選んでください')
   if self.path=='/api/map-cells':
    raise ValueError('マス対応付けはJSON APIで実行してください')
   if self.path=='/api/layout':
    try:
     from pipeline import process
    except ImportError:
     self.send(503,{'error':'画像補正には pip install opencv-python-headless numpy が必要です'});return
    self.send(200,process(image));return
   reqbody={'model':os.getenv('SCORECLEAN_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':PROMPT},{'role':'user','content':[{'type':'text','text':'Read this baseball scorebook and output JSON only.'},{'type':'image_url','image_url':{'url':'data:'+mime+';base64,'+base64.b64encode(image).decode()}}]}],'response_format':{'type':'json_object'},'max_tokens':6000}
   req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=json.dumps(reqbody).encode(),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=110) as r:answer=json.load(r)
   raw=answer['choices'][0]['message']['content'];self.send(200,{'result':json.loads(raw)})
  except (ValueError,KeyError,json.JSONDecodeError) as e:self.send(400,{'error':str(e)})
  except urllib.error.HTTPError as e:self.send(502,{'error':f'AI API error {e.code}: '+e.read().decode()[:350]})
  except Exception as e:self.send(502,{'error':str(e)})
if __name__=='__main__':
 print('ScoreClean: http://localhost:8765 (AI requires OPENAI_API_KEY and internet)')
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
