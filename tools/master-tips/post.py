"""Пост «советы мастера»: мультяшный мастер сверху, тёмная панель с темой, советами и ценой.
python3 post.py img.jpg out.jpg "Имя" "Тема" "совет1|совет2|совет3" "60 мин — 27 000 ₸ · 90 мин — 37 000 ₸"
"""
import sys
from PIL import Image, ImageDraw, ImageFont
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
BG=(12,28,22); GOLD=(214,180,110)
def wrap(d,t,f,w):
    out=[];line=''
    for x in t.split():
        if line and d.textlength(line+' '+x,font=f)>w: out.append(line); line=x
        else: line=(line+' '+x).strip()
    return out+[line]
def post(src,out,name,topic,tips,price):
    W,H=1080,1350; tips=tips.split('|')
    ph=760; im=Image.open(src).convert('RGB'); s=max(W/im.width,ph/im.height)
    im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    x0=(im.width-W)//2; y0=min(int(im.height*0.06),im.height-ph); im=im.crop((x0,y0,x0+W,y0+ph))
    c=Image.new('RGB',(W,H),BG); c.paste(im,(0,0))
    g=Image.new('L',(1,H))
    for y in range(H): g.putpixel((0,y),int(min(255,max(0,(y-560)*1.3))))
    c=Image.composite(Image.new('RGB',(W,H),BG),c,g.resize((W,H)))
    d=ImageDraw.Draw(c)
    d.text((70,700),f'СОВЕТЫ МАСТЕРА · {name.upper()}',font=ImageFont.truetype(FB,32),fill=GOLD)
    d.text((66,745),topic,font=ImageFont.truetype(SER,84),fill=(250,240,220))
    f=ImageFont.truetype(FM,38); y=870
    for i,t in enumerate(tips):
        d.ellipse((72,y+12,90,y+30),fill=GOLD)
        for j,l in enumerate(wrap(d,t,f,880)):
            d.text((110,y),l,font=f,fill=(238,232,222)); y+=50
        y+=18
    f=ImageFont.truetype(FB,34); tw=d.textlength(price,font=f)
    d.rounded_rectangle((60,1262,60+tw+56,1318),28,fill=GOLD); d.text((88,1270),price,font=f,fill=BG)
    c.save(out,quality=92)
if __name__=='__main__': post(*sys.argv[1:])
