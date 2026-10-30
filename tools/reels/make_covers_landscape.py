import sys; sys.path.insert(0,'/home/user/thepalm-media/tools/reels')
import cover_overlay as mkov
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
R='/home/user/thepalm-media/images/reels/'
def cover(n,look,l1,l2,y0,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    src=Image.open(f'look_{look}.img').convert('RGB'); w,h=src.size
    k=max(1080/w,1920/h); bg=src.resize((int(w*k),int(h*k))); x=(bg.width-1080)//2
    bg=bg.crop((x,0,x+1080,1920)).filter(ImageFilter.GaussianBlur(30))
    k=1250/h; fg=src.resize((int(w*k),1250),Image.LANCZOS); x=(fg.width-1080)//2+y0
    fg=fg.crop((x,0,x+1080,1250)).convert('RGBA')
    import numpy as np
    a=np.full((1250,1080),255.0); a[1000:]*=np.linspace(1,0,250)[:,None]
    fg.putalpha(Image.fromarray(a.astype('uint8')))
    im=bg.convert('RGBA'); im.alpha_composite(fg)
    im=ImageEnhance.Brightness(im.convert('RGB')).enhance(0.85).convert('RGBA')
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    d=Image.new('RGBA',(1080,1920),(10,8,6,255)); d.putalpha(Image.eval(v,lambda p:int((255-p)*0.5)))
    im.alpha_composite(d); im.alpha_composite(Image.open(f'ov{n}.png'))
    im.convert('RGB').save(out,quality=90)
cover(15,'a30c2e06','Спорим, не скажу «ай»?','Огненный массаж',-150,R+'abylai-ep15-cover.jpg')
cover(16,'a547c822','Кто дольше в сауне?','3 правила сауны',0,R+'abylai-ep16-cover.jpg')
cover(17,'3798aed6','Проигравший —','под веник',0,R+'abylai-ep17-cover.jpg')
cover(18,'f334f429','4 руки — это вдвое?','Массаж в 4 руки',0,R+'abylai-ep18-cover.jpg')
cover(19,'249c941d','Пари проиграл,','спину выиграл',0,R+'abylai-ep19-cover.jpg')
s=Image.new('RGB',(1800,640))
for i,k in enumerate((15,16,17,18,19)): s.paste(Image.open(R+f'abylai-ep{k}-cover.jpg').resize((360,640)),(360*i,0))
s.save('csheet.jpg')
