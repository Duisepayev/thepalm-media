import json, sys, time, urllib.request, concurrent.futures as cf
H='https://api.heygen.com'
RAW='https://raw.githubusercontent.com/Duisepayev/thepalm-media/claude/project-thread-mv1io2/images/reels/'
DIANA=('e0caf722b56e44d9a2c5276feeef8059','UsZXAP2XiyeLBCWww6Ar')
ERLAN=('048309abbb3942768e372643e08e3151','2cc79ea86d244d5f8116c86151f8d756')
def api(p,b=None):
    r=urllib.request.Request(H+p,data=json.dumps(b).encode() if b else None,headers={'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r))
def gen(job):
    name,who,bg,text=job
    tp,voice=DIANA if who=='D' else ERLAN
    body={'video_inputs':[{'character':{'type':'talking_photo','talking_photo_id':tp,'use_avatar_iv_model':True,'matting':True},
        'voice':{'type':'text','voice_id':voice,'input_text':text,'speed':1.1 if who=='D' else 1.0},
        'background':{'type':'image','url':RAW+bg}}],'dimension':{'width':1080,'height':1920},'title':name}
    vid=api('/v2/video/generate',body)['data']['video_id']
    for _ in range(120):
        d=api(f'/v1/video_status.get?video_id={vid}')['data']
        if d['status']=='completed':
            urllib.request.urlretrieve(d['video_url'],name+'.mp4'); return name,'ok'
        if d['status']=='failed': return name,str(d.get('error'))
        time.sleep(10)
    return name,'timeout'
jobs=json.load(open(sys.argv[1]))
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(gen,jobs): print(*r)
