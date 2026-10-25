"""Карточка мастера для Instagram в едином стиле (тёмная панель снизу).

python3 tools/master-card/make.py <фото> <выход.jpg> "Имя" "2 года" "Процедура 1" ... (до 4)
Фото: портрет мастера, верх кадра идёт в зону 1080×900.
"""
import html, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageFilter

here = os.path.dirname(os.path.abspath(__file__))
photo, out, name, exp, *items = sys.argv[1:]
tmp = tempfile.mkdtemp()
im = Image.open(photo).convert('RGB')
im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
if im.height < 900:
    im = Image.open(photo).convert('RGB')
    im = im.resize((round(im.width * 900 / im.height), 900), Image.LANCZOS)
    x = (im.width - 1080) // 2
    im = im.crop((x, 0, x + 1080, 900))
im = im.filter(ImageFilter.UnsharpMask(2, 60, 2)).crop((0, 0, 1080, 900))
im.save(os.path.join(tmp, 'photo.jpg'), quality=95)
shutil.copy(os.path.join(here, 'icon.png'), tmp)
page = open(os.path.join(here, 'card.html'), encoding='utf-8').read()
page = (page.replace('{{NAME}}', html.escape(name)).replace('{{EXP}}', html.escape(exp))
        .replace('{{ITEMS}}', ''.join(f'<li>{html.escape(i)}</li>' for i in items)))
open(os.path.join(tmp, 'card.html'), 'w', encoding='utf-8').write(page)
js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
      "const p=await b.newPage({viewport:{width:1080,height:1350}});"
      f"await p.goto('file://{tmp}/card.html');await p.waitForTimeout(2500);"
      f"await p.screenshot({{path:'{tmp}/out.png'}});await b.close()}})();")
subprocess.run(['node', '-e', js], check=True)
Image.open(os.path.join(tmp, 'out.png')).convert('RGB').save(out, quality=92)
print(out)
