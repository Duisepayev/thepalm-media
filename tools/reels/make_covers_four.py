import os,sys
sys.path.insert(0,'/home/user/thepalm-media/tools/reels')
os.chdir('/tmp/claude-0/erlan/cut')
exec(open('/home/user/thepalm-media/tools/reels/make_covers.py').read().split("R='/home/user")[0])
def place(base,name,FW,cx,fy,tint):
    im,(x,y,w,h)=cut(name); s=FW/w
    im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    arr=np.asarray(im).astype(float); arr[...,:3]*=np.array(tint); im=Image.fromarray(np.clip(arr,0,255).astype('uint8'),'RGBA')
    ox=int(cx-(x+w/2)*s); oy=int(fy-(y+h/2)*s)
    al=np.asarray(im.split()[3]).astype(float); H=al.shape[0]; yy=np.arange(H)[:,None]
    Wd=al.shape[1]; xx=np.arange(Wd)[None,:]; al*=np.clip((H*0.97-yy)/(H*0.28),0,1); al*=np.clip((xx-2)/(Wd*0.12),0,1)*np.clip((Wd-2-xx)/(Wd*0.12),0,1); al*=np.clip((1500-(yy+oy))/350,0,1)
    im.putalpha(Image.fromarray(al.astype('uint8')))
    base.alpha_composite(im,(ox,oy))
R='/home/user/thepalm-media/images/reels/'
W=(1.0,0.96,0.9); C=(0.92,0.96,1.05)
def cover4(n,scene,ids,l1,l2,tint,out):
    mkov.make(n,l1,l2,f'ov{n}.png')
    sc=Image.open(glob.glob(f'{T}/mcp-Figma-blob-*-{scene}.png')[0]).convert('RGB').resize((1080,1935),Image.LANCZOS).crop((0,0,1080,1920))
    sc=ImageEnhance.Brightness(sc.filter(ImageFilter.GaussianBlur(4))).enhance(0.72).convert('RGBA')
    t=tuple(x*0.93 for x in tint)
    a,b,c_,d=ids  # left-front, mid-left back, mid-right back, right-front
    place(sc,b,175,415,455,t); place(sc,c_,175,665,455,t)
    place(sc,a,190,175,560,t); place(sc,d,190,905,560,t)
    v=Image.new('L',(1080,1920),0); ImageDraw.Draw(v).ellipse((-300,-200,1380,1700),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    dd=Image.new('RGBA',(1080,1920),(10,8,6,255)); dd.putalpha(Image.eval(v,lambda p:int((255-p)*0.5)))
    sc.alpha_composite(dd); sc.alpha_composite(Image.open(f'ov{n}.png'))
    sc.convert('RGB').save(out,quality=90)
cover4(25,'1rkl02',['e848bc4e','624723da','a0e7a2d1','73388404'],'Кто больше устал?','Каждому свой массаж',W,R+'abylai-ep25-cover.jpg')
cover4(26,'acjvz0',['2212b42b','624723da','a0e7a2d1','3ca8eb0f'],'Саят получил инвестиции!','Авторская программа',W,R+'abylai-ep26-cover.jpg')
cover4(27,'x2ktvs',['2212b42b','624723da','a0e7a2d1','804cdc12'],'Спорим, не усну?','Массаж стоп и головы',C,R+'abylai-ep27-cover.jpg')
cover4(28,'lmu1da',['e848bc4e','624723da','a0e7a2d1','3ca8eb0f'],'Будни 10–17: −10%.','Все вместе и дешевле',W,R+'abylai-ep28-cover.jpg')
cover4(29,'1rkl02',['b9ee337a','50a3fa2c','a1bca4ec','91de3991'],'Мужской вечер.','Сауна и массаж',W,R+'abylai-ep29-cover.jpg')
cover4(30,'acjvz0',['2212b42b','624723da','a0e7a2d1','73388404'],'Финал сезона.','До встречи во 2-м сезоне',W,R+'abylai-ep30-cover.jpg')
s=Image.new('RGB',(2160,640))
for i,k in enumerate(range(25,31)): s.paste(Image.open(R+f'abylai-ep{k}-cover.jpg').resize((360,640)),(360*i,0))
s.save('/tmp/claude-0/erlan/ep2530/csheet.jpg')
