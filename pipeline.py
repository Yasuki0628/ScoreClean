"""Optional OpenCV perspective rectification and ruled-grid estimation."""
import base64
import cv2
import numpy as np

def process(data):
    im=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
    if im is None: raise ValueError('画像を開けません')
    h,w=im.shape[:2]
    if max(h,w)>2200:
        k=2200/max(h,w);im=cv2.resize(im,None,fx=k,fy=k)
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0)
    edges=cv2.Canny(blur,55,150)
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    corners=None
    for c in sorted(contours,key=cv2.contourArea,reverse=True)[:35]:
        p=cv2.approxPolyDP(c,.025*cv2.arcLength(c,True),True)
        if len(p)==4 and cv2.contourArea(p)>.25*im.shape[0]*im.shape[1] and cv2.isContourConvex(p):
            corners=p.reshape(4,2).astype('float32');break
    if corners is not None:
        sums=corners.sum(1);diff=np.diff(corners,axis=1).ravel()
        src=np.array([corners[np.argmin(sums)],corners[np.argmin(diff)],corners[np.argmax(sums)],corners[np.argmax(diff)]],dtype='float32')
        tw=max(np.linalg.norm(src[1]-src[0]),np.linalg.norm(src[2]-src[3]));th=max(np.linalg.norm(src[3]-src[0]),np.linalg.norm(src[2]-src[1]))
        tw=int(np.clip(tw,400,2200));th=int(np.clip(th,400,3000))
        dst=np.array([[0,0],[tw-1,0],[tw-1,th-1],[0,th-1]],dtype='float32')
        im=cv2.warpPerspective(im,cv2.getPerspectiveTransform(src,dst),(tw,th),borderValue=(255,255,255))
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    bw=cv2.adaptiveThreshold(g,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,31,10)
    hh,ww=bw.shape
    vertical=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,max(18,hh//16))))
    horizontal=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(max(18,ww//18),1)))
    def peaks(proj,limit):
        threshold=max(limit,float(np.max(proj))*.22)
        ids=np.where(proj>threshold)[0];groups=[]
        for i in ids:
            if not groups or i>groups[-1][-1]+2:groups.append([int(i)])
            else:groups[-1].append(int(i))
        return [round(sum(a)/len(a)) for a in groups if len(a)>=1]
    xs=peaks((vertical>0).sum(0),hh*.18)
    ys=peaks((horizontal>0).sum(1),ww*.18)
    ok,buf=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,88])
    if not ok:raise ValueError('補正画像を作れません')
    return {'image':'data:image/jpeg;base64,'+base64.b64encode(buf).decode(),'width':ww,'height':hh,'verticalLines':xs,'horizontalLines':ys,'perspectiveDetected':corners is not None,'confidence':'要確認' if len(xs)<6 or len(ys)<10 else '罫線候補検出','warning':'罫線には文字線が混入する場合があります。必ず確認してください。'}
