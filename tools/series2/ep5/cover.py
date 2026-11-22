import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
n='5'; T='4 утра после тоя'; S='/tmp/claude-0/-home-user/fa883927-edfa-5f1c-9e31-1c33427ecd5c/scratchpad/ep5'
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
im=Image.open(S+'/coverbg.jpg').convert('RGB').resize((1080,1935)).crop((0,0,1080,1920)); W,H=im.size
dark=Image.new('RGB',(W,H),(10,24,18))
g=Image.new('L',(1,H)); g2=Image.new('L',(1,H))
for y in range(H): g.putpixel((0,y), int(max(0,220*(1-y/520)))); g2.putpixel((0,y), int(min(230,max(0,(y-1500)*0.6))))
im=Image.composite(dark,im,g.resize((W,H))); im=Image.composite(dark,im,g2.resize((W,H)))
d=ImageDraw.Draw(im)
def ctext(t,y,f,col,glow=False):
    global d
    tw=d.textlength(t,font=f); x=(W-tw)/2
    if glow:
        l=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(l).text((x,y),t,font=f,fill=(230,190,110,255))
        l=l.filter(ImageFilter.GaussianBlur(14)); im.paste(l,(0,0),l); d=ImageDraw.Draw(im)
    d.text((x,y),t,font=f,fill=col)
ctext('THE PALM',100,ImageFont.truetype(SER,160),(250,236,205),glow=True)
ctext('сериал · 24/7',300,ImageFont.truetype(FM,40),(230,215,185))
ctext('СЕРИЯ '+n,1650,ImageFont.truetype(FB,54),(214,180,110))
ctext(T,1720,ImageFont.truetype(FB,84),(255,255,255))
im.save(S+'/cover-ep5.jpg',quality=92); im.resize((360,640)).save(S+'/cover-pv.jpg')
