import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0,'.'); import mkov
def cover(n,look,l1,l2,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    im=Image.open(look).convert('RGB'); w,h=im.size
    im=im.resize((1080,int(h*1080/w)),Image.LANCZOS).crop((0,0,1080,1920))
    base=ImageEnhance.Brightness(im).enhance(0.92).convert('RGBA')
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    d2=Image.new('RGBA',(1080,1920),(10,8,6,255)); d2.putalpha(Image.eval(v,lambda p:int((255-p)*0.45)))
    base.alpha_composite(d2); base.alpha_composite(Image.open(f'ov{n}.png'))
    base.convert('RGB').save(out,quality=90)
R='/home/user/thepalm-media/images/reels/'
cover(6,'dy_804cdc12.jpg','После футбола.','Спортивный массаж ног',R+'abylai-ep6-cover.jpg')
cover(7,'dy_91de3991.jpg','«Не усну ни за что»','Массаж стоп',R+'abylai-ep7-cover.jpg')
cover(8,'dy_3ca8eb0f.jpg','«Просто мимо проходил»','Массаж банками',R+'abylai-ep8-cover.jpg')
cover(9,'dy_73388404.jpg','Целая команда.','Будни 10–17: −10%',R+'abylai-ep9-cover.jpg')
s=Image.new('RGB',(1800,640))
for i,n in enumerate(range(5,10)): s.paste(Image.open(R+f'abylai-ep{n}-cover.jpg').resize((360,640)),(360*i,0))
s.save('sheet59.jpg')
