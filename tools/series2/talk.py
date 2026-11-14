import json, sys, time, urllib.request, concurrent.futures as cf
H='https://api.heygen.com'
AV={'alina':'29ef764de4d6318afe70680c721b6edb','aisha':'84c2563e829f809efd015353f7677ef0','mary':'30f270c5b80ae339418147af9b86c1a6','zhibek':'72b95c30d7f735bdbd02ba924a71b1db'}
VO={'alina':'cb404f2d35334184839c66cbab7937b2','aisha':'e73c775c2e6f4400a125dd6ee2f07e2e','mary':'0052fdde677d465f909aa182e6ce3232','zhibek':'655364e79506483a8f768ba50199cbb4'}
def api(p,b=None):
    r=urllib.request.Request(H+p,data=json.dumps(b).encode() if b else None,headers={'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r))
def gen(job):
    name,who,text=job
    body={'video_inputs':[{'character':{'type':'talking_photo','talking_photo_id':AV[who],'use_avatar_iv_model':True},
        'voice':{'type':'text','voice_id':VO[who],'input_text':text}}],'dimension':{'width':720,'height':1280},'title':'ep1 '+name}
    try: vid=api('/v2/video/generate',body)['data']['video_id']
    except urllib.error.HTTPError as e: return name,e.read()[:300]
    for _ in range(180):
        d=api(f'/v1/video_status.get?video_id={vid}')['data']
        if d['status']=='completed':
            urllib.request.urlretrieve(d['video_url'],name+'.mp4'); return name,'ok'
        if d['status']=='failed': return name,str(d.get('error'))
        time.sleep(10)
    return name,'timeout'
jobs=json.load(open(sys.argv[1]))
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(gen,jobs): print(*r, flush=True)
