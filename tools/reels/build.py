"""Сборка рилса: ИИ-ведущая в начале и в конце, в середине кадры салона под её голос.

python3 tools/reels/build.py plan.json out.mp4
plan.json: {"host": "диана.mp4", "segments": [{"src": "host"|"файл", "start": c, "dur": c}],
            "captions": [[t0, t1, "текст"]], "ai_label": true,
            "music": "трек.mp3", "music_vol": 0.12, "music_start": 8}
Звук всегда целиком из host, видео по сегментам подряд. Титры рисуются Pillow (Inter Bold).
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_S = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'


def run(*a):
    subprocess.run(a, check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', path]).decode())


def caption_png(text, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 64)
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > W - 200 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    lh = 84
    y = int(H * 0.68) - len(lines) * lh // 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = (W - tw) / 2
        d.rounded_rectangle((x - 28, y - 10, x + tw + 28, y + lh - 6), 18, fill=(43, 29, 20, 215))
        d.text((x, y), ln, font=f, fill=(251, 244, 234))
        y += lh
    im.save(path)


def label_png(path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_S, 30)
    t = 'Ведущая создана ИИ'
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((W - tw - 76, 60, W - 40, 112), 14, fill=(0, 0, 0, 110))
    d.text((W - tw - 58, 68), t, font=f, fill=(255, 255, 255, 230))
    im.save(path)


def main():
    plan_path, out = sys.argv[1:3]
    plan = json.load(open(plan_path, encoding='utf-8'))
    base = os.path.dirname(os.path.abspath(plan_path))
    host = os.path.join(base, plan['host'])
    # кадр ведущей должен стоять там же, где звучит её голос, иначе губы не совпадут
    t = 0
    for s in plan['segments']:
        if s['src'] == 'host' and abs(s['start'] - t) > 0.05:
            sys.exit(f'ведущая с {s["start"]} с стоит на {t:.2f} с: губы разойдутся с голосом')
        src = host if s['src'] == 'host' else os.path.join(base, s['src'])
        if s['start'] + s['dur'] > duration(src) + 0.01:
            sys.exit(f'{s["src"]}: {s["start"]}+{s["dur"]} с длиннее самого клипа, ролик укоротится')
        t += s['dur']
    tmp = tempfile.mkdtemp()
    parts = []
    for i, s in enumerate(plan['segments']):
        src = host if s['src'] == 'host' else os.path.join(base, s['src'])
        p = f'{tmp}/s{i}.mp4'
        # zoom > 1 приближает кадр, y — где резать по вертикали (0 верх, 0.5 центр)
        z, y = s.get('zoom', 1), s.get('y', 0.5)
        fit = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
        if z != 1:
            fit += f',scale={round(W * z)}:{round(H * z)},crop={W}:{H}:(iw-{W})/2:(ih-{H})*{y}'
        if s.get('vf'):
            fit += ',' + s['vf']
        run('ffmpeg', '-v', 'error', '-ss', str(s['start']), '-t', str(s['dur']), '-i', src, '-an',
            '-vf', f'{fit},fps={FPS},setsar=1',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-y', p)
        parts.append(p)
    with open(f'{tmp}/list.txt', 'w') as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    run('ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/list.txt', '-c', 'copy', '-y', f'{tmp}/v.mp4')

    inputs, chain, last = ['-i', f'{tmp}/v.mp4', '-i', host], [], '0:v'
    n = 2
    for j, (t0, t1, text) in enumerate(plan['captions']):
        caption_png(text, f'{tmp}/c{j}.png')
        inputs += ['-i', f'{tmp}/c{j}.png']
        chain.append(f"[{last}][{n}:v]overlay=0:0:enable='gte(t,{t0})*lt(t,{t1})'[o{j}]")
        last, n = f'o{j}', n + 1
    if plan.get('ai_label'):
        label_png(f'{tmp}/ai.png')
        inputs += ['-i', f'{tmp}/ai.png']
        chain.append(f'[{last}][{n}:v]overlay=0:0[oai]')
        last = 'oai'
    audio = '1:a'
    if plan.get('music'):
        # музыка фоном под голос: тихо, по кругу, затухает в последние 1,5 с
        dur = duration(host)
        inputs += ['-stream_loop', '-1', '-ss', str(plan.get('music_start', 0)), '-i', os.path.join(base, plan['music'])]
        vol = plan.get('music_vol', 0.12)
        chain.append(f"[{n}:a]volume={vol},afade=t=in:d=0.5,afade=t=out:st={dur - 1.5}:d=1.5[mus]")
        chain.append('[1:a][mus]amix=inputs=2:duration=first:normalize=0[aout]')
        audio = '[aout]'
    run('ffmpeg', '-v', 'error', *inputs, '-filter_complex', ';'.join(chain), '-map', f'[{last}]', '-map', audio,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
        '-shortest', '-movflags', '+faststart', '-y', out)
    print(out)


main()
