import json,sys,subprocess
# avatar.py name file.jpg -> prints talking_photo id
name,f=sys.argv[1],sys.argv[2]
r=json.loads(subprocess.check_output(['curl','-s','-X','POST','https://api.heygen.com/v3/assets','-F',f'file=@{f};type=image/jpeg']))
aid=(r.get('data') or {}).get('asset_id') or (r.get('data') or {}).get('id')
if not aid: print('ERR asset',r); sys.exit(1)
b=json.dumps({'type':'photo','name':name,'file':{'type':'asset_id','asset_id':aid}})
r=json.loads(subprocess.check_output(['curl','-s','-X','POST','https://api.heygen.com/v3/avatars','-H','Content-Type: application/json','-d',b]))
print(name, json.dumps(r)[:600])
