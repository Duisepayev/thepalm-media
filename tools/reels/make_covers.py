import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
sys.path.insert(0,'.'); import mkov
FACE={'ab_e848bc4e':(.52,.27,.42),'ab_2212b42b':(.55,.30,.45),'ab_eed1d0c7':(.55,.30,.45),'dy_39bbc71e':(.52,.30,.27),
'dy_804cdc12':(.52,.17,.24),'dy_91de3991':(.48,.30,.30),'dy_3ca8eb0f':(.48,.35,.28),'dy_73388404':(.48,.32,.39)}
BG=(14,11,8)
def panel(name,FW=360,FY=430):
    cx,cy,fw=FACE[name]; im=Image.open(name+'.jpg').convert('RGB'); w,h=im.size
    s=FW/(fw*w); im=im.resize((int(w*s),int(h*s)),Image.LANCZOS); W,H=im.size
    fy=min(FY,cy*H); ox=int(300-cx*W); oy=int(fy-cy*H)
    p=Image.new('RGB',(600,1920),BG); a=np.ones((H,W))
    fade=min(260,H//4); a[H-fade:]=np.linspace(1,0,fade)[:,None]
    p.paste(im,(ox,oy),Image.fromarray((a*255).astype('uint8')))
    return p
def cover(n,ab,dy,l1,l2,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    L=panel(ab); R=panel(dy)
    base=Image.new('RGB',(1080,1920),BG); base.paste(R,(480,0))
    x=np.arange(600)[None,:]; y=np.arange(1920)[:,None]
    m=np.clip(((540+(y-960)*0.06)-x)/40+0.5,0,1)
    base.paste(L,(0,0),Image.fromarray((m*255).astype('uint8')))
    base=ImageEnhance.Brightness(base).enhance(0.93).convert('RGBA')
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    d2=Image.new('RGBA',(1080,1920),(10,8,6,255)); d2.putalpha(Image.eval(v,lambda p:int((255-p)*0.45)))
    base.alpha_composite(d2); base.alpha_composite(Image.open(f'ov{n}.png'))
    base.convert('RGB').save(out,quality=90)
R='/home/user/thepalm-media/images/reels/'
cover(5,'ab_e848bc4e','dy_39bbc71e','«Массаж для бабушек?»','Классический массаж',R+'abylai-ep5-cover.jpg')
cover(6,'ab_2212b42b','dy_804cdc12','После футбола.','Спортивный массаж ног',R+'abylai-ep6-cover.jpg')
cover(7,'ab_2212b42b','dy_91de3991','«Не усну ни за что»','Массаж стоп',R+'abylai-ep7-cover.jpg')
cover(8,'ab_e848bc4e','dy_3ca8eb0f','«Просто мимо проходил»','Массаж банками',R+'abylai-ep8-cover.jpg')
cover(9,'ab_eed1d0c7','dy_73388404','Целая команда.','Будни 10–17: −10%',R+'abylai-ep9-cover.jpg')
s=Image.new('RGB',(1800,640))
for i,k in enumerate(range(5,10)): s.paste(Image.open(R+f'abylai-ep{k}-cover.jpg').resize((360,640)),(360*i,0))
s.save('duo.jpg')
