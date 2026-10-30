import sys; sys.path.insert(0,'/home/user/thepalm-media/tools/reels')
import cover_overlay as mkov
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
R='/home/user/thepalm-media/images/reels/'
def cover(n,look,l1,l2,y0,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    im=Image.open(f'look_{look}.img').convert('RGB'); w,h=im.size
    s=1080/w; im=im.resize((1080,int(h*s)),Image.LANCZOS)
    im=im.crop((0,y0,1080,y0+1920)); im=ImageEnhance.Brightness(im).enhance(0.85).convert('RGBA')
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    d=Image.new('RGBA',(1080,1920),(10,8,6,255)); d.putalpha(Image.eval(v,lambda p:int((255-p)*0.5)))
    im.alpha_composite(d); im.alpha_composite(Image.open(f'ov{n}.png'))
    im.convert('RGB').save(out,quality=90)
cover(10,'3cbaacee','Прилетел ночью.','Лимфодренаж ног',0,R+'abylai-ep10-cover.jpg')
cover(11,'c2daba58','3 часа ночи, не уснуть.','Массаж головы',0,R+'abylai-ep11-cover.jpg')
s=Image.new('RGB',(720,640))
for i,k in enumerate((10,11)): s.paste(Image.open(R+f'abylai-ep{k}-cover.jpg').resize((360,640)),(360*i,0))
s.save('csheet.jpg')
