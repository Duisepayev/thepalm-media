import sys, glob, numpy as np
from PIL import Image, ImageDraw, ImageFont
T='/root/.claude/projects/-home-user-thepalm-media/fa883927-edfa-5f1c-9e31-1c33427ecd5c/tool-results'
F='/tmp/claude-0/erlan/cov/fonts/package/files/montserrat-%s-%d-normal.woff'
GOLD=(201,168,107,255); GREY=(86,83,80,255)
def font(w,size): return ImageFont.truetype(F%('cyrillic',w),size), ImageFont.truetype(F%('latin',w),size)
def draw_text(d,x,y,text,w,size,fill,spacing=0):
    cy,la=font(w,size)
    for ch in text:
        f=cy if ('Ѐ'<=ch<='ӿ') else la
        d.text((x,y),ch,font=f,fill=fill); x+=f.getlength(ch)+spacing
    return x
def make(n,l1,l2,out):
    o=np.array(Image.open(glob.glob(T+'/mcp-Figma-blob-*-96kd01.png')[0]).convert('RGBA'))
    for y in range(1375,1920): o[y,:1040]=o[y,1060]
    im=Image.fromarray(o); d=ImageDraw.Draw(im)
    for i in range(30):
        x=70+31*i; d.rounded_rectangle((x,1380,x+24,1389),radius=3,fill=GOLD if i<n else GREY)
    label=f'СЕРИЯ {n}'
    cy,la=font(800,44); w=sum((cy if 'Ѐ'<=c<='ӿ' else la).getlength(c)+4 for c in label)-4
    pw=int(w+66); d.rounded_rectangle((70,1418,70+pw,1500),radius=41,fill=GOLD)
    draw_text(d,103,1433,label,800,44,(30,24,18,255),spacing=4)
    draw_text(d,70,1528,l1,400,60,(255,255,255,255))
    draw_text(d,70,1598,l2,400,60,(255,255,255,255))
    im.save(out)
if __name__=='__main__': make(int(sys.argv[1]),sys.argv[2],sys.argv[3],sys.argv[4])
