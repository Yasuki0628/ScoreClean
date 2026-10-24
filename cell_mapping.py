"""Geometry-first cell assignment with explicit ambiguity handling."""
import math

def map_cells(layout, observations, *, row_start=0, col_start=0, rows=9, cols=6, side='away'):
    xs=sorted(set(int(x) for x in layout.get('verticalLines', [])))
    ys=sorted(set(int(y) for y in layout.get('horizontalLines', [])))
    if len(xs)<cols+1 or len(ys)<rows+1:
        return {'mapped':{},'review':[{'reason':'罫線不足','observation':o} for o in observations], 'cells':[], 'status':'needs_grid_review'}
    # Caller must supply the first boundary indices of the batting area; do not guess from full-page lines.
    if row_start<0 or col_start<0 or len(xs)<col_start+cols+1 or len(ys)<row_start+rows+1:
        return {'mapped':{},'review':[{'reason':'表の開始位置が不正','observation':o} for o in observations], 'cells':[], 'status':'needs_grid_review'}
    x=xs[col_start:col_start+cols+1];y=ys[row_start:row_start+rows+1]
    cells=[{'key':f'{side}:{r}:{c}','row':r,'inning':c,'bbox':[x[c],y[r],x[c+1],y[r+1]]} for r in range(rows) for c in range(cols)]
    mapped={};review=[]
    for obs in observations:
        bbox=obs.get('bbox')
        if not isinstance(bbox,list) or len(bbox)!=4:
            review.append({'reason':'座標なし','observation':obs});continue
        a,b,d,e=map(float,bbox)
        if a>=d or b>=e:
            review.append({'reason':'座標不正','observation':obs});continue
        area=(d-a)*(e-b)
        overlaps=[]
        for cell in cells:
            u,v,w,z=cell['bbox'];overlap=max(0,min(d,w)-max(a,u))*max(0,min(e,z)-max(b,v))
            if overlap>0:overlaps.append((overlap/area,cell['key']))
        overlaps.sort(reverse=True)
        confidence=float(obs.get('confidence',0))
        if not overlaps or overlaps[0][0]<.65 or confidence<.7 or (len(overlaps)>1 and overlaps[1][0]>.25):
            review.append({'reason':'境界跨ぎ・低信頼度','observation':obs,'candidates':overlaps[:3]});continue
        key=overlaps[0][1]
        if key in mapped:
            review.append({'reason':'同じマスに複数候補','observation':obs,'existing':mapped.pop(key)});continue
        mapped[key]={'result':str(obs.get('result',''))[:20],'note':str(obs.get('note',''))[:100],'bases':min(4,max(0,int(obs.get('bases',0)))),'out':str(obs.get('out','')) if str(obs.get('out','')) in ('1','2','3') else '', 'sourceBBox':bbox,'confidence':confidence}
    return {'mapped':mapped,'review':review,'cells':cells,'status':'review_required'}
