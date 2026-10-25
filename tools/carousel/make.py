"""Слайды карусели для Instagram в стиле карточек The Palm (1080×1350 JPEG).

python3 tools/carousel/make.py carousels.json [slug ...]
Берёт карусели из carousels.json (все или перечисленные slug), рисует слайды в
images/carousels/<slug>-NN.jpg и записывает список файлов в поле images.
Типы слайдов: cover, text, list, steps, offer, cta. Фото — из site/assets/img.
"""
import html, json, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageFilter

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
img_dir = os.path.join(root, 'site', 'assets', 'img')
out_dir = os.path.join(root, 'images', 'carousels')
e = html.escape

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Inter,sans-serif}
.dark{background:#2b1d14;color:#f6efe4}.light{background:#f4ece0;color:#2b1d14}
.photo{position:absolute;left:0;top:0;width:1080px;background-position:center;background-size:cover}
.logo{position:absolute;left:64px;top:55px;display:flex;align-items:flex-start;gap:12px}
.logo img{height:62px;margin-top:2px}
.lm{font-family:Lora,serif;font-size:37px;line-height:1;margin-top:4px}
.ls{font-size:14.5px;letter-spacing:4.6px;color:#c9a46a;margin-top:9px}
.light .lm{color:#2b1d14}.light .ls{color:#9a7442}.dark .lm{color:#f6efe4}
.page{position:absolute;right:64px;top:70px;font-size:22px;letter-spacing:3px;color:#b08a55}
.kicker{font-size:25px;letter-spacing:7px;font-weight:500;color:#c8ac85;text-transform:uppercase}
.light .kicker{color:#9a7442}
h1{font-family:Lora,serif;font-weight:400;line-height:1.08}
h2{font-family:Lora,serif;font-weight:400;font-size:92px;line-height:1.08}
.box{position:absolute;left:64px;right:64px}
.body{font-size:44px;line-height:1.42}
.light .body{color:#4a3526}.dark .body{color:#efe5d6}
.line{width:90px;height:2px;background:#c1a16e;margin:44px 0}
ul{list-style:none}
li{font-size:44px;line-height:1.36;padding-left:50px;position:relative;margin-bottom:40px}
li:before{content:"";position:absolute;left:4px;top:23px;width:15px;height:15px;border-radius:50%;background:#c8954f}
ol{list-style:none;counter-reset:n}
ol li{padding-left:106px;min-height:76px}
ol li:before{counter-increment:n;content:counter(n);width:74px;height:74px;top:-6px;left:0;border:2px solid #b08a55;background:none;
  border-radius:50%;font-family:Lora,serif;font-size:38px;line-height:70px;text-align:center;color:#9a7442}
.dark ol li:before{color:#e3c597}
.swipe{position:absolute;right:64px;bottom:64px;font-size:24px;letter-spacing:4px;color:#e3c597}
.light .swipe{color:#9a7442}
.prices{margin-top:34px}
.pr{display:flex;justify-content:space-between;align-items:baseline;font-size:34px;padding:20px 0;border-bottom:1px solid rgba(201,164,106,.35)}
.pr b{font-family:Lora,serif;font-weight:400;font-size:44px;color:#e3c597;white-space:nowrap;margin-left:30px}
.note{font-size:25px;line-height:1.45;color:#c8ac85;margin-top:28px}
.pill{display:inline-block;padding:0 28px;height:58px;line-height:55px;border:1.5px solid #b08a55;border-radius:30px;color:#e3c597;font-size:27px;margin:0 14px 18px 0}
.foot{font-size:28px;line-height:1.6;color:#efe5d6}
"""
LOGO = ('<div class="logo"><img src="icon.png"><div><div class="lm">The Palm</div>'
        '<div class="ls">MASSAGE &amp; SPA</div></div></div>')


def photo(name, w, h, dst):
    im = Image.open(os.path.join(img_dir, name)).convert('RGB')
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    im.crop((x, y, x + w, y + h)).filter(ImageFilter.UnsharpMask(2, 60, 2)).save(dst, quality=95)


def slide(s, i, n, tmp):
    t = s['type']
    page = f'<div class="page">{i}/{n}</div>'
    if t == 'cover':
        photo(s['photo'], 1080, 1350, os.path.join(tmp, f'p{i}.jpg'))
        size = s.get('size', 104)
        return ('dark', f"""<div class="photo" style="height:1350px;background-image:url(p{i}.jpg)"></div>
<div class="photo" style="height:1350px;background:linear-gradient(180deg,rgba(43,29,20,.55) 0%,rgba(43,29,20,.05) 25%,rgba(43,29,20,.25) 45%,rgba(43,29,20,.92) 72%,#2b1d14 100%)"></div>
{LOGO}<div class="box" style="bottom:150px"><div class="kicker">{e(s.get('kicker', ''))}</div>
<h1 style="font-size:{size}px;margin-top:26px;color:#fbf4ea">{e(s['title'])}</h1>
<div class="body" style="margin-top:30px;color:#e9dccb">{e(s.get('sub', ''))}</div></div>
<div class="swipe">ЛИСТАЙТЕ →</div>""")
    if t in ('text', 'list', 'steps'):
        theme = s.get('theme', 'light')
        inner = ''
        if s.get('body'):
            inner += ''.join(f'<p class="body" style="margin-bottom:34px">{e(p)}</p>' for p in s['body'].split('\n'))
        if s.get('items'):
            tag = 'ol' if t == 'steps' else 'ul'
            inner += f'<{tag}>' + ''.join(f'<li>{e(x)}</li>' for x in s['items']) + f'</{tag}>'
        return (theme, f"""{LOGO}{page}<div class="box" style="top:240px"><div class="kicker">{e(s.get('kicker', ''))}</div>
<h2 style="margin-top:22px">{e(s['title'])}</h2><div class="line"></div>{inner}</div>""")
    if t == 'offer':
        photo(s['photo'], 1080, 600, os.path.join(tmp, f'p{i}.jpg'))
        rows = ''.join(f'<div class="pr"><span>{e(a)}</span><b>{e(b)}</b></div>' for a, b in s['prices'])
        note = f'<div class="note">{e(s["note"])}</div>' if s.get('note') else ''
        return ('dark', f"""<div class="photo" style="height:600px;background-image:url(p{i}.jpg)"></div>
<div class="photo" style="height:601px;background:linear-gradient(180deg,rgba(43,29,20,.45) 0%,rgba(43,29,20,0) 25%,rgba(43,29,20,0) 60%,#2b1d14 100%)"></div>
{LOGO}{page}<div class="box" style="top:585px"><div class="kicker">{e(s.get('kicker', 'Решение'))}</div>
<h2 style="margin-top:18px;font-size:68px">{e(s['title'])}</h2>
<div class="body" style="font-size:30px;margin-top:18px;color:#d9c9b4">{e(s.get('sub', ''))}</div>
<div class="prices">{rows}</div>{note}</div>""")
    if t == 'cta':
        photo(s.get('photo', 'robes.webp'), 1080, 520, os.path.join(tmp, f'p{i}.jpg'))
        return ('dark', f"""<div class="photo" style="height:520px;background-image:url(p{i}.jpg)"></div>
<div class="photo" style="height:521px;background:linear-gradient(180deg,rgba(43,29,20,.45) 0%,rgba(43,29,20,0) 25%,rgba(43,29,20,0) 55%,#2b1d14 100%)"></div>
{LOGO}{page}<div class="box" style="top:500px"><div class="kicker">The Palm massage &amp; spa</div>
<h2 style="margin-top:18px">{e(s.get('title', 'Запишитесь в WhatsApp'))}</h2>
<div class="body" style="margin-top:20px;color:#d9c9b4">{e(s.get('sub', 'Ссылка в шапке профиля. Подберём программу и мастера.'))}</div>
<div style="margin-top:36px"><span class="pill">−10% на первое посещение</span><span class="pill">−10% по будням 10:00–17:00</span></div>
<div class="note" style="margin-top:4px">Скидки не суммируются.</div>
<div class="line" style="margin:34px 0 26px"></div>
<div class="foot">Аль-Фараби 41/7, ЖК Metropole, блок 7<br>Круглосуточно, 24/7 · +7 778 580 58 32</div></div>""")
    raise ValueError(t)


def render(c, tmp):
    n = len(c['slides'])
    files = []
    for i, s in enumerate(c['slides'], 1):
        theme, body = slide(s, i, n, tmp)
        doc = (f'<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?'
               f'family=Lora:wght@400;500&family=Inter:wght@400;500&display=swap" rel="stylesheet">'
               f'<style>{CSS}</style></head><body class="{theme}">{body}</body></html>')
        open(os.path.join(tmp, f's{i}.html'), 'w', encoding='utf-8').write(doc)
        files.append(f"{c['slug']}-{i:02d}.jpg")
    return files


def main():
    path, *only = sys.argv[1:]
    data = json.load(open(path, encoding='utf-8'))
    os.makedirs(out_dir, exist_ok=True)
    jobs = []
    for c in data:
        c['images'] = [f"{c['slug']}-{i:02d}.jpg" for i in range(1, len(c['slides']) + 1)]
        if only and c['slug'] not in only:
            continue
        tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(here, 'icon.png'), tmp)
        render(c, tmp)
        jobs.append((c, tmp))
    pages = [(f'{tmp}/s{i}.html', f'{tmp}/s{i}.png') for c, tmp in jobs for i in range(1, len(c['slides']) + 1)]
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:1080,height:1350}});"
          f"for(const [h,o] of {json.dumps(pages)}){{await p.goto('file://'+h);"
          "await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({path:o});}"
          "await b.close()})();")
    subprocess.run(['node', '-e', js], check=True)
    for c, tmp in jobs:
        for i, f in enumerate(c['images'], 1):
            Image.open(f'{tmp}/s{i}.png').convert('RGB').save(os.path.join(out_dir, f), quality=90)
        print(c['slug'], len(c['images']))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


main()
