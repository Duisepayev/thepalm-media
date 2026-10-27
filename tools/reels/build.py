"""Сборка рилса: ИИ-ведущая в начале и в конце, в середине кадры салона под её голос.

python3 tools/reels/build.py plan.json out.mp4
plan.json: {"host": "диана.mp4", "segments": [{"src": "host"|"файл", "start": c, "dur": c}],
            "captions": [[t0, t1, "текст"]], "ai_label": true}
Звук всегда целиком из host, видео по сегментам подряд. Титры рисуются Pillow (Inter Bold).
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_S = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'


def run(*a):
    subprocess.run(a, check=True)


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
        chain.append(f"[{last}][{n}:v]overlay=0:0:enable='between(t,{t0},{t1})'[o{j}]")
        last, n = f'o{j}', n + 1
    if plan.get('ai_label'):
        label_png(f'{tmp}/ai.png')
        inputs += ['-i', f'{tmp}/ai.png']
        chain.append(f'[{last}][{n}:v]overlay=0:0[oai]')
        last = 'oai'
    run('ffmpeg', '-v', 'error', *inputs, '-filter_complex', ';'.join(chain), '-map', f'[{last}]', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
        '-shortest', '-movflags', '+faststart', '-y', out)
    print(out)


main()
