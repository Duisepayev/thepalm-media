import subprocess, json, os
from PIL import Image, ImageDraw, ImageFont
W,H=720,1280
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FM='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
def wrap(d,t,f,maxw):
    out=[];cur=''
    for w in t.split():
        n=(cur+' '+w).strip()
        if d.textlength(n,font=f)>maxw and cur: out.append(cur); cur=w
        else: cur=n
    out.append(cur); return out
def sub_png(name,text,top=None,tag=None,size=40):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if text:
        f=ImageFont.truetype(FB,size); lines=wrap(d,text,f,W-120)
        lh=size+12; y=H-300-len(lines)*lh
        for ln in lines:
            tw=d.textlength(ln,font=f); x=(W-tw)/2
            d.rounded_rectangle((x-16,y-6,x+tw+16,y+lh-4),12,fill=(0,0,0,150))
            d.text((x,y),ln,font=f,fill=(255,255,255))
            y+=lh
    if top:
        f=ImageFont.truetype(FB,44); tw=d.textlength(top,font=f)
        d.rounded_rectangle(((W-tw)/2-22,90,(W+tw)/2+22,156),16,fill=(20,60,40,200))
        d.text(((W-tw)/2,98),top,font=f,fill=(251,244,234))
    if tag:
        f=ImageFont.truetype(FM,26); tw=d.textlength(tag,font=f)
        d.text((W-tw-36,44),tag,font=f,fill=(255,255,255,220))
    im.save(name)
def endpng(name):
    from PIL import ImageFilter
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
    def c(t,y,f,col,glow=None):
        tw=d.textlength(t,font=f); x=(W-tw)/2
        if glow:
            l=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(l).text((x,y),t,font=f,fill=glow)
            l=l.filter(ImageFilter.GaussianBlur(12)); im.alpha_composite(l)
        d.text((x,y),t,font=f,fill=col)
    c('Кто он?',150,ImageFont.truetype(SER,110),(250,236,205,255),(230,190,110,255))
    c('Смотрите завтра в 22:00',300,ImageFont.truetype(FB,42),(214,180,110,255))
    band=Image.new('RGBA',(W,300),(8,20,15,200)); im.alpha_composite(band,(0,H-300))
    c('The Palm · 24/7',H-260,ImageFont.truetype(FB,40),(251,244,234,255))
    c('Запись в WhatsApp',H-200,ImageFont.truetype(FM,32),(230,220,200,255))
    c('+7 778 580 58 32',H-150,ImageFont.truetype(FB,44),(214,180,110,255))
    im.save(name)
def card(name):
    im=Image.new('RGB',(W,H),(18,40,30)); d=ImageDraw.Draw(im)
    def c(t,y,f,col=(251,244,234)):
        tw=d.textlength(t,font=f); d.text(((W-tw)/2,y),t,font=f,fill=col)
    c('Кто он?',420,ImageFont.truetype(FB,96))
    c('Смотрите завтра в 22:00',560,ImageFont.truetype(FB,44),(214,180,110))
    c('«Смена» · серия 2',630,ImageFont.truetype(FM,34))
    c('The Palm · 24/7',880,ImageFont.truetype(FB,40))
    c('Запись в WhatsApp',950,ImageFont.truetype(FM,34))
    c('+7 778 580 58 32',1000,ImageFont.truetype(FB,40))
    im.save(name)
SEQ=json.load(open('seq.json'))
parts=[]
for i,s in enumerate(SEQ):
    png=f'o{i}.png'; sub_png(png,s.get('sub'),s.get('top'),None)
    out=f'p{i}.mp4'; pad=',tpad=start_mode=clone:start_duration=0.5' if i==0 else ''
    vf=f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1{pad}[v];[v][1:v]overlay=0:0[o]"
    vol=s.get('vol',1.0)
    cmd=['ffmpeg','-loglevel','error','-y','-i',s['clip'],'-i',png,'-filter_complex',vf+f";[0:a]volume={vol},aresample=48000,aformat=channel_layouts=stereo{',adelay=500:all=1' if i==0 else ''}[a]",'-map','[o]','-map','[a]']
    if s.get('dur'): cmd+=['-t',str(s['dur'])]
    cmd+=['-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-c:a','aac','-b:a','160k',out]
    subprocess.run(cmd,check=True); parts.append(out)
endpng('end.png')
subprocess.run(['ffmpeg','-loglevel','error','-y','-i','end.mp4','-loop','1','-i','end.png','-filter_complex',f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=1.5[v];[1:v]format=rgba,fade=t=in:st=1.2:d=0.8:alpha=1[t];[v][t]overlay=0:0:shortest=1[o];[0:a]volume=0.5,aresample=48000,aformat=channel_layouts=stereo,apad[a]",'-map','[o]','-map','[a]','-t','6.5','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-c:a','aac','-b:a','160k','pcard.mp4'],check=True)
parts.append('pcard.mp4')
open('list.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','raw.mp4'],check=True)
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','raw.mp4']))
subprocess.run(['ffmpeg','-loglevel','error','-y','-i','raw.mp4','-stream_loop','-1','-ss','8','-i','m_velario.mp3','-filter_complex',f"[1:a]volume=0.13,afade=t=out:st={dur-2}:d=2[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]",'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(dur),'ep1.mp4'],check=True)
print('done',dur)
