import json, sys, time, urllib.request, concurrent.futures as cf
H='https://api.heygen.com'
RAW='https://raw.githubusercontent.com/Duisepayev/thepalm-media/claude/project-thread-mv1io2/images/reels/'
DIANA=('e0caf722b56e44d9a2c5276feeef8059','UsZXAP2XiyeLBCWww6Ar')
AVOICE='f3aa6db808fb4348a8591358cfe8b564'
def api(p,b=None):
    r=urllib.request.Request(H+p,data=json.dumps(b).encode() if b else None,headers={'Content-Type':'application/json'})
    try: return json.load(urllib.request.urlopen(r))
    except urllib.error.HTTPError as e: raise SystemExit(e.read().decode())
def gen(job):
    name,who,text=job
    if who=='D':
        vi={'character':{'type':'talking_photo','talking_photo_id':DIANA[0],'use_avatar_iv_model':True,'matting':True},
            'voice':{'type':'text','voice_id':DIANA[1],'input_text':text,'speed':1.1},
            'background':{'type':'image','url':RAW+'bg-reception.jpg'}}
    else:
        vi={'character':{'type':'talking_photo','talking_photo_id':who,'use_avatar_iv_model':True},
            'voice':{'type':'text','voice_id':AVOICE,'input_text':text,'speed':1.0}}
    vid=api('/v2/video/generate',{'video_inputs':[vi],'dimension':{'width':1080,'height':1920},'title':name})['data']['video_id']
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
