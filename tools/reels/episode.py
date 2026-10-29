"""Серия по описанию: части (ролики HeyGen) → host.mp4, кадры по фразам → build.py.
ep.py spec.json out.mp4 (в папке со спецификацией лежат части и клипы)
spec: {"music_start": 60, "parts": [{"name": "e2d1", "say": ["фраза"], "caps": ["титр"], "show": ["host" | [клипы]]}]}
клип: {"src", "at", "zoom"?, "y"?, "vf"?}; на фразу клипы делят её время поровну.
"""
import json, os, re, subprocess, sys

def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

def starts(path, say):
    log = subprocess.run(['ffmpeg', '-i', path, '-af', 'silencedetect=n=-30dB:d=0.2', '-f', 'null', '-'], capture_output=True, text=True).stderr
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', log)]
    total = dur(path); chars = [len(s) for s in say]; out, acc = [0.0], 0
    for c in chars[:-1]:
        acc += c; g = total * acc / sum(chars)
        near = min((e for e in ends if e > out[-1] + 0.4), key=lambda e: abs(e - g), default=g)
        out.append(near if abs(near - g) < 1.5 else g)
    return out + [total]

spec_path, out = sys.argv[1:3]
spec = json.load(open(spec_path)); base = os.path.dirname(os.path.abspath(spec_path)); os.chdir(base)
for p in spec['parts']:
    if not os.path.exists('n_' + p['name'] + '.mp4'):
        subprocess.run(['ffmpeg', '-v', 'error', '-i', p['name'] + '.mp4', '-vf', 'scale=1080:1920,fps=30,setsar=1', '-c:v', 'libx264', '-crf', '16',
                        '-preset', 'fast', '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-b:a', '192k', '-y', 'n_' + p['name'] + '.mp4'], check=True)
slug = os.path.splitext(os.path.basename(out))[0]
open(slug + '-list.txt', 'w').writelines(f"file 'n_{p['name']}.mp4'\n" for p in spec['parts'])
host = slug + '-host.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', slug + '-list.txt', '-c', 'copy', '-y', host], check=True)
segs, caps, off = [], [], 0.0
for p in spec['parts']:
    b = starts('n_' + p['name'] + '.mp4', p['say'])
    for i in range(len(p['say'])):
        t0, t1 = off + b[i], off + b[i + 1]
        caps.append([round(t0, 3), round(t1, 3), p['caps'][i]])
        show = p['show'][i]
        if show == 'host':
            segs.append({'src': 'host', 'start': round(t0, 3), 'dur': round(t1 - t0, 3), 'zoom': p.get('zoom',1.3), 'y': p.get('y',0.1)})
        else:
            n = len(show); d = (t1 - t0) / n
            for c in show:
                c = dict(c); c['start'] = c.pop('at'); c['dur'] = round(d, 3); segs.append(c)
    off += b[-1]
# склейка должна совпасть с длиной голоса
t = 0
for s in segs:
    if s['src'] == 'host': s['start'] = round(t, 3)
    t += s['dur']
segs[-1]['dur'] = round(segs[-1]['dur'] + dur(host) - t, 3)
plan = {'host': host, 'music': 'm_velario.mp3', 'music_vol': 0.16, 'music_start': spec.get('music_start', 60), 'segments': segs, 'captions': caps}
json.dump(plan, open(slug + '-plan.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build.py'), slug + '-plan.json', out], check=True)
