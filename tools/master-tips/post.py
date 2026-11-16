"""Пост «советы мастера»: мультяшный мастер сверху, тёмная панель с темой, советами и ценой.
python3 post.py img.jpg out.jpg "Имя" "Тема" "совет1|совет2|совет3" "60 мин — 27 000 ₸ · 90 мин — 37 000 ₸"
"""
import sys
from PIL import Image, ImageDraw, ImageFont
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
BG=(43,29,20); GOLD=(214,180,110)
def wrap(d,t,f,w):
    out=[];line=''
    for x in t.split():
        if line and d.textlength(line+' '+x,font=f)>w: out.append(line); line=x
        else: line=(line+' '+x).strip()
    return out+[line]
def post(src,out,name,topic,tips,price,prog=None):
    W,H=1080,1350; tips=tips.split('|')
    ph=760; im=live_top(src,prog) if prog else Image.open(src).convert('RGB'); s=max(W/im.width,ph/im.height)
    im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    x0=(im.width-W)//2; y0=min(int(im.height*0.06),im.height-ph); im=im.crop((x0,y0,x0+W,y0+ph))
    c=Image.new('RGB',(W,H),BG); c.paste(im,(0,0))
    g=Image.new('L',(1,H))
    for y in range(H): g.putpixel((0,y),int(min(255,max(0,(y-560)*1.3))))
    c=Image.composite(Image.new('RGB',(W,H),BG),c,g.resize((W,H)))
    d=ImageDraw.Draw(c)
    d.text((70,700),f'СОВЕТЫ МАСТЕРА · {name.upper()}',font=ImageFont.truetype(FB,32),fill=GOLD)
    sz=84
    while d.textlength(topic,font=ImageFont.truetype(SER,sz))>950: sz-=2
    d.text((66,745+(84-sz)//2),topic,font=ImageFont.truetype(SER,sz),fill=(250,240,220))
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

def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    return m

def fill(im, w, h, fy=0.4):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * fy); return im.crop((x, y, x + w, y + h))

def live_top(master, prog, out_w=1080, out_h=760):
    """Живое фото: слева портрет мастера, справа фото программы."""
    c = fill(Image.open(prog).convert('RGB'), out_w, out_h, 0.5)
    pw, ph = 400, 520
    p = fill(Image.open(master).convert('RGB'), pw, ph, 0.0)
    bd = Image.new('RGB', (pw + 12, ph + 12), GOLD)
    c.paste(bd, (48, 60), rounded(bd, 30)); c.paste(p, (54, 66), rounded(p, 26))
    return c

def cover_live(master, prog, out):
    """Обложка карусели 1080×1350: фото программы + портрет мастера в рамке справа сверху."""
    c = fill(Image.open(prog).convert('RGB'), 1080, 1350, 0.3)
    pw, ph = 420, 540
    p = fill(Image.open(master).convert('RGB'), pw, ph, 0.0)
    bd = Image.new('RGB', (pw + 12, ph + 12), GOLD)
    c.paste(bd, (1080 - pw - 66, 130), rounded(bd, 30)); c.paste(p, (1080 - pw - 60, 136), rounded(p, 26))
    c.save(out, quality=95)
