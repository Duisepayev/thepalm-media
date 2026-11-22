import json, sys, time, urllib.request, concurrent.futures as cf
H='https://api.heygen.com'
AV={'olzhasB3':'0098f6df2f1a0ae2f41878956b36075e','aishaC3':'12b7c10294e59ab5b8912c05208552f8','aishaK2':'ebbf8c019b9aaca2c345f8d5b278beba','olzhasB':'2f5ff5d39163619967585b15b8457b2b','aishaC':'94d47324c3d5c7b482ebc59b851403ec','madina':'08fdf604a359ad80c9479dffa39db68b','zhadyra':'54f97261caabac9953ccc41b84fd2ae3','olzhasJ':'7e5576b621fd058064ea2d28a70b9d1d','aishaK':'c2f3f54876ea9b38ab864916c0f4233d','dimashV':'2f5ff5d39163619967585b15b8457b2b','zhadyraV':'54f97261caabac9953ccc41b84fd2ae3','olzhasV':'2f5ff5d39163619967585b15b8457b2b','mary4':'7623340a2123e1816313a4f63d30c017','zhibek4':'da255165cf1e9a79cc925bc1a957055a','aisha4':'44bf022708680f2d757b44b9c8734d91','erzhan':'c6f0a9e138285193c10418c8a330a1b5','aisha3':'5a05415d86e63f418dca5a739b9cdfd3','mary3':'1b13012825c8836d7d6da7beaaf1f620','roland3':'687e52c1a206450f1264766539cfabae','zhibek3':'80c3a33b7944d1bdd5a6a676dc5f3240','mary3b':'68aa9b1c0d2c302fc9259abcea2701fa','roland':'c268e9330c5b1440416fa4ffd538967a','aisha2':'975afd6256f79a592235f429c03f213a','alina':'29ef764de4d6318afe70680c721b6edb','aisha':'84c2563e829f809efd015353f7677ef0','mary':'30f270c5b80ae339418147af9b86c1a6','zhibek':'72b95c30d7f735bdbd02ba924a71b1db'}
VO={'olzhasB3':'d7c91f5e68db45c180f555f5e3b8552f','aishaC3':'e73c775c2e6f4400a125dd6ee2f07e2e','aishaK2':'e73c775c2e6f4400a125dd6ee2f07e2e','olzhasB':'d7c91f5e68db45c180f555f5e3b8552f','olzhasJ':'d7c91f5e68db45c180f555f5e3b8552f','olzhasV':'d7c91f5e68db45c180f555f5e3b8552f','aishaC':'e73c775c2e6f4400a125dd6ee2f07e2e','aishaK':'e73c775c2e6f4400a125dd6ee2f07e2e','madina':'cc484a0bd95445c589a86316513cc64c','zhadyra':'86c8273fd10b407092f725aa3d9ebb4a','zhadyraV':'86c8273fd10b407092f725aa3d9ebb4a','dimashV':'b94b0dda433d40c38b92290eba94484a','mary4':'0052fdde677d465f909aa182e6ce3232','zhibek4':'655364e79506483a8f768ba50199cbb4','aisha4':'e73c775c2e6f4400a125dd6ee2f07e2e','erzhan':'d7c91f5e68db45c180f555f5e3b8552f','aisha3':'e73c775c2e6f4400a125dd6ee2f07e2e','aisha2':'e73c775c2e6f4400a125dd6ee2f07e2e','mary3':'0052fdde677d465f909aa182e6ce3232','mary3b':'0052fdde677d465f909aa182e6ce3232','roland':'1ac556ee67df4d8b8fdbdd8b32f0bb02','roland3':'1ac556ee67df4d8b8fdbdd8b32f0bb02','zhibek3':'655364e79506483a8f768ba50199cbb4','alina':'cb404f2d35334184839c66cbab7937b2','aisha':'e73c775c2e6f4400a125dd6ee2f07e2e','mary':'0052fdde677d465f909aa182e6ce3232','zhibek':'655364e79506483a8f768ba50199cbb4'}
def api(p,b=None,_n=0):
    r=urllib.request.Request(H+p,data=json.dumps(b).encode() if b else None,headers={'Content-Type':'application/json'})
    try: return json.load(urllib.request.urlopen(r))
    except urllib.error.HTTPError as e:
        if e.code>=500 and _n<5: time.sleep(5); return api(p,b,_n+1)
        raise
def gen(job):
    name,who,text=job
    body={'video_inputs':[{'character':{'type':'talking_photo','talking_photo_id':AV[who],'use_avatar_iv_model':True},
        'voice':{'type':'text','voice_id':VO[who],'input_text':text}}],'dimension':{'width':720,'height':1280},'title':'ep5 '+name}
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
