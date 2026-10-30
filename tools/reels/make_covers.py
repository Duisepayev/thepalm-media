import sys, glob, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0,'/tmp/claude-0/erlan/cov2'); import mkov
T='/root/.claude/projects/-home-user-thepalm-media/fa883927-edfa-5f1c-9e31-1c33427ecd5c/tool-results'
def cut(name):
    g=np.asarray(Image.open(name+'.png').convert('RGB')).astype(float)
    r,gg,b=g[...,0],g[...,1],g[...,2]
    a=1-np.clip((gg-np.maximum(r,b))/60.0,0,1)
    g[...,1]=np.minimum(gg,np.maximum(r,b)*1.05)
    im=Image.fromarray(np.dstack([g,a*255]).astype('uint8'),'RGBA')
    im.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(1.2)))
    A=a>0.5; rows=np.where(A.sum(1)>20)[0]; y0=rows[0]
    ws=[];cs=[]
    for y in range(y0+60,y0+180):
        xs=np.where(A[y])[0]; ws.append(xs[-1]-xs[0]); cs.append((xs[-1]+xs[0])/2)
    w=float(np.median(ws)); cx=float(np.median(cs))
    return im,(cx-w/2,y0+0.95*w-w/2,w,w)
def place(base,name,FW,cx,fy,tint):
    im,(x,y,w,h)=cut(name); s=FW/w
    im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    arr=np.asarray(im).astype(float); arr[...,:3]*=np.array(tint); im=Image.fromarray(np.clip(arr,0,255).astype('uint8'),'RGBA')
    ox=int(cx-(x+w/2)*s); oy=int(fy-(y+h/2)*s)
    # bottom fade
    al=np.asarray(im.split()[3]).astype(float); H=al.shape[0]; yy=np.arange(H)[:,None]+oy
    al*=np.clip((1500-yy)/350,0,1); im.putalpha(Image.fromarray(al.astype('uint8')))
    base.alpha_composite(im,(ox,oy))
def cover(n,scene,left,right,l1,l2,tint,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    sc=Image.open(glob.glob(f'{T}/mcp-Figma-blob-*-{scene}.png')[0]).convert('RGB').resize((1080,1935),Image.LANCZOS).crop((0,0,1080,1920))
    sc=ImageEnhance.Brightness(sc.filter(ImageFilter.GaussianBlur(4))).enhance(0.72).convert('RGBA')
    place(sc,right,250,770,500,tuple(t*0.93 for t in tint))
    place(sc,left,228,320,480,tuple(t*0.93 for t in tint))
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    d=Image.new('RGBA',(1080,1920),(10,8,6,255)); d.putalpha(Image.eval(v,lambda p:int((255-p)*0.5)))
    sc.alpha_composite(d); sc.alpha_composite(Image.open(f'ov{n}.png'))
    sc.convert('RGB').save(out,quality=90)
R='/home/user/thepalm-media/images/reels/'
W=(1.0,0.96,0.9); C=(0.92,0.96,1.05)
cover(5,'lmu1da','e848bc4e','39bbc71e','«Массаж для бабушек?»','Классический массаж',W,R+'abylai-ep5-cover.jpg')
cover(6,'x2ktvs','2212b42b','804cdc12','После футбола.','Спортивный массаж ног',C,R+'abylai-ep6-cover.jpg')
cover(7,'1rkl02','2212b42b','91de3991','Не может уснуть.','Массаж стоп',W,R+'abylai-ep7-cover.jpg')
cover(8,'acjvz0','e848bc4e','3ca8eb0f','Спину тянет.','Массаж банками',W,R+'abylai-ep8-cover.jpg')
cover(9,'emhdow','2212b42b','73388404','Вся команда.','Будни 10–17: −10%',W,R+'abylai-ep9-cover.jpg')
s=Image.new('RGB',(1800,640))
for i,k in enumerate(range(5,10)): s.paste(Image.open(R+f'abylai-ep{k}-cover.jpg').resize((360,640)),(360*i,0))
s.save('sheet.jpg')
