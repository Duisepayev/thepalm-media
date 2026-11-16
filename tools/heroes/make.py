import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
def card(src,out,name,role,fact):
    W,H=1080,1350
    im=Image.open(src).convert('RGB')
    s=max(W/im.width, 1000/im.height); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    x=(im.width-W)//2; im=im.crop((x,0,x+W,1000))
    c=Image.new('RGB',(W,H),(12,28,22)); c.paste(im,(0,0))
    g=Image.new('L',(1,H))
    for y in range(H): g.putpixel((0,y),int(min(255,max(0,(y-760)*1.1))))
    c=Image.composite(Image.new('RGB',(W,H),(12,28,22)),c,g.resize((W,H)))
    top=Image.new('L',(1,H))
    for y in range(H): top.putpixel((0,y),int(max(0,170*(1-y/230))))
    c=Image.composite(Image.new('RGB',(W,H),(12,28,22)),c,top.resize((W,H)))
    d=ImageDraw.Draw(c)
    f=ImageFont.truetype(SER,64); t='СМЕНА'; d.text(((W-d.textlength(t,font=f))/2,40),t,font=f,fill=(240,215,160))
    f=ImageFont.truetype(FM,30); t='герои сериала The Palm'; d.text(((W-d.textlength(t,font=f))/2,118),t,font=f,fill=(225,210,180))
    f=ImageFont.truetype(FB,96); d.text((70,980),name,font=f,fill=(255,255,255))
    f=ImageFont.truetype(FB,36); d.text((72,1095),role.upper(),font=f,fill=(214,180,110))
    f=ImageFont.truetype(FM,38); y=1155
    words=fact.split(); line=''
    for w in words:
        if d.textlength(line+' '+w,font=f)>940: d.text((72,y),line.strip(),font=f,fill=(235,230,220)); y+=50; line=''
        line+=' '+w
    d.text((72,y),line.strip(),font=f,fill=(235,230,220))
    f=ImageFont.truetype(FB,30); t='Сериал «Смена» · с 28 ноября в 22:00'
    d.rounded_rectangle((60,1272,60+d.textlength(t,font=f)+48,1322),25,fill=(214,180,110))
    d.text((84,1279),t,font=f,fill=(12,28,22))
    c.save(out,quality=92)
if __name__=='__main__': card(*sys.argv[1:])
