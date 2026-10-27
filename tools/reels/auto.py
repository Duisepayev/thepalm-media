"""Рилс по сценарию одной командой: голос Дианы в HeyGen → раскладка кадров → build.py.

python3 tools/reels/auto.py spec.json workdir out.mp4
spec.json: {"slug": "reel11-head", "say": ["фраза", ...], "caps": ["титр", ...],
            "pool": ["p9186.mp4", ...], "intro": 1, "outro": 2, "mid": 3, "music_start": 30}
say и caps идут парами: титр висит, пока звучит его фраза. intro — сколько первых фраз Диана
говорит в кадре, outro — сколько последних, mid — номер фразы, на которой она мелькает в середине.
Клипы из pool лежат в workdir, кадры по ~1,5 с берутся по кругу из середины каждого клипа.
"""
import json, os, random, re, subprocess, sys, time, urllib.request

HEYGEN = 'https://api.heygen.com'
BG = 'https://raw.githubusercontent.com/Duisepayev/thepalm-media/claude/project-thread-mv1io2/images/reels/bg-reception.jpg'
CUT = 1.5


def api(path, body=None):
    req = urllib.request.Request(HEYGEN + path, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req))


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', path]).decode())


def diana(text, path):
    if os.path.exists(path):
        return
    body = {'video_inputs': [{
        'character': {'type': 'talking_photo', 'talking_photo_id': 'e0caf722b56e44d9a2c5276feeef8059',
                      'use_avatar_iv_model': True, 'matting': True},
        'voice': {'type': 'text', 'voice_id': 'UsZXAP2XiyeLBCWww6Ar', 'input_text': text, 'speed': 1.1},
        'background': {'type': 'image', 'url': BG}}],
        'dimension': {'width': 1080, 'height': 1920}, 'title': os.path.basename(path)}
    vid = api('/v2/video/generate', body)['data']['video_id']
    for _ in range(90):
        d = api(f'/v1/video_status.get?video_id={vid}')['data']
        if d['status'] == 'completed':
            urllib.request.urlretrieve(d['video_url'], path)
            return
        if d['status'] == 'failed':
            sys.exit(f'HeyGen: {d}')
        time.sleep(10)
    sys.exit('HeyGen: не дождались видео')


def sentence_starts(host, say):
    """Начало каждой фразы: ожидаемое время по длине текста, притянутое к ближайшей паузе."""
    log = subprocess.run(['ffmpeg', '-i', host, '-af', 'silencedetect=n=-30dB:d=0.15', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', log)]
    total = duration(host)
    chars = [len(s) for s in say]
    starts, acc = [0.0], 0
    for c in chars[:-1]:
        acc += c
        guess = total * acc / sum(chars)
        near = min((e for e in ends if e > starts[-1] + 0.5), key=lambda e: abs(e - guess), default=guess)
        starts.append(near if abs(near - guess) < 2.0 else guess)
    return starts, total


def main():
    spec_path, work, out = sys.argv[1:4]
    spec = json.load(open(spec_path, encoding='utf-8'))
    say, caps = spec['say'], spec['caps']
    host = os.path.join(work, spec['slug'] + '-diana.mp4')
    diana(' '.join(say), host)
    starts, total = sentence_starts(host, say)
    bounds = starts + [total]
    rnd = random.Random(spec['slug'])
    pool = spec['pool'][:]
    rnd.shuffle(pool)
    clip_i = 0

    def clips(t0, t1):
        nonlocal clip_i
        segs, t = [], t0
        while t1 - t > 0.05:
            d = CUT if t1 - t > CUT + 0.8 else t1 - t
            item = pool[clip_i % len(pool)]
            clip_i += 1
            # клип в pool — имя файла или {"src", "zoom", "y", "vf"} для кадра с поправкой
            item = dict(item) if isinstance(item, dict) else {'src': item}
            length = duration(os.path.join(work, item['src']))
            lo, hi = length * 0.1, max(length * 0.1, length * 0.9 - d)
            # at — проверенный момент клипа, когда в остальном кадре есть то, что показывать нельзя
            start = item.pop('at', None)
            start = min(start, length - d) if start is not None else rnd.uniform(lo, hi)
            segs.append({**item, 'start': round(start, 2), 'dur': round(d, 3)})
            t += d
        return segs

    def on_host(t0, t1):
        return [{'src': 'host', 'start': round(t0, 3), 'dur': round(t1 - t0, 3), 'zoom': 1.3, 'y': 0.1}]

    intro_end = min(bounds[spec.get('intro', 1)], 3.2)
    outro_start = bounds[len(say) - spec.get('outro', 2)]
    segs = on_host(0, intro_end)
    mid = spec.get('mid')
    if mid is not None and bounds[mid] > intro_end + 1 and bounds[mid + 1] < outro_start - 1:
        a, b = bounds[mid], min(bounds[mid + 1], bounds[mid] + 3.0)
        segs += clips(intro_end, a) + on_host(a, b) + clips(b, outro_start)
    else:
        segs += clips(intro_end, outro_start)
    segs += on_host(outro_start, total)
    # склеенная длина должна совпасть с голосом до кадра
    drift = total - sum(s['dur'] for s in segs)
    segs[-1]['dur'] = round(segs[-1]['dur'] + drift, 3)

    plan = {'host': os.path.basename(host), 'music': 'm_velario.mp3', 'music_vol': 0.16,
            'music_start': spec.get('music_start', 15), 'segments': segs,
            'captions': [[round(bounds[i], 2), round(bounds[i + 1], 2), caps[i]] for i in range(len(say))]}
    plan_path = os.path.join(work, spec['slug'] + '-plan.json')
    json.dump(plan, open(plan_path, 'w'), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'build.py'), plan_path, out], check=True)


main()
