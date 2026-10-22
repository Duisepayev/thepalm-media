#!/usr/bin/env python3
"""Сборка сайта thepalm.kz из data/*.json в dist/.

Только стандартная библиотека Python: Cloudflare Pages запускает `python3 build.py`.
`python3 build.py --preview` делает ссылки вида .../index.html для просмотра без сервера.
"""
import html
import json
import os
import posixpath
import shutil
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
PREVIEW = "--preview" in sys.argv


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


S = load("settings.json")
MASTERS = load("masters.json")["masters"]
PROGRAMS_DATA = load("programs.json")
PROGRAMS = PROGRAMS_DATA["programs"]
ALTEGIO = {s["id"]: s for s in load("altegio-services.json")["services"]}
BLOG = load("blog.json")["posts"]

GROUPS = [
    ("massage", "Массаж"),
    ("spa", "SPA-программы"),
    ("extra", "Сауна и SPA-услуги"),
]

e = html.escape


# ---------- данные ----------

def price_of(item):
    if "altegio_id" in item:
        svc = ALTEGIO.get(item["altegio_id"])
        if not svc or not svc["active"]:
            raise SystemExit(f"Услуга {item['altegio_id']} ({item['label']}) не найдена или выключена в Altegio")
        return svc["price"]
    return item["price"]


def fmt(n):
    return f"{n:,}".replace(",", " ") + " ₸"


def min_price(p):
    return min(price_of(x) for x in p["prices"])


def by_slug(slug):
    return next(p for p in PROGRAMS if p["slug"] == slug)


def wa_link(topic=None):
    text = S["whatsapp_text"] + (f" Хочу записаться: {topic}." if topic else " Хочу записаться.")
    return f"https://wa.me/{S['whatsapp']}?text={quote(text)}"


# ---------- ссылки ----------

class Page:
    def __init__(self, path):
        self.path = path  # "/", "/mastera/", ...

    def url(self, target):
        """Относительная ссылка с текущей страницы на target ("/mastera/" или "/assets/x.css")."""
        here = self.path if self.path.endswith("/") else posixpath.dirname(self.path) + "/"
        rel = posixpath.relpath(target, here)
        if target.endswith("/"):
            rel = "" if rel == "." else rel + "/"
            if PREVIEW:
                rel += "index.html"
            elif rel == "":
                rel = "./"
        return rel


# ---------- куски разметки ----------

ICON_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7.5-.1 1.5-.6 1.8-1.2.2-.6.2-1.1.1-1.2l-.5-.2Z"/></svg>'
ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2Z"/></svg>'


def btn_wa(label="Записаться в WhatsApp", topic=None, where="", cls="btn btn-primary"):
    return (f'<a class="{cls}" href="{e(wa_link(topic))}" target="_blank" rel="noopener" '
            f'data-track="whatsapp_click" data-where="{e(where)}" data-topic="{e(topic or "")}">{ICON_WA}<span>{e(label)}</span></a>')


def btn_call(label="Позвонить", where="", cls="btn btn-ghost"):
    return (f'<a class="{cls}" href="tel:{S["phone_href"]}" data-track="phone_click" data-where="{e(where)}">'
            f'{ICON_PHONE}<span>{e(label)}</span></a>')


def jsonld():
    data = {
        "@context": "https://schema.org",
        "@type": "DaySpa",
        "name": S["name"],
        "url": S["domain"] + "/",
        "telephone": S["phone_href"],
        "email": S["email"],
        "image": S["domain"] + "/assets/img/reception.webp",
        "priceRange": "₸₸",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": S["address"],
            "addressLocality": S["city"],
            "addressCountry": "KZ",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": S["geo"]["lat"], "longitude": S["geo"]["lon"]},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        }],
        "sameAs": [S["instagram"], S["tiktok"]],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def layout(pg, title, description, body, image="reception.webp"):
    gtm = S.get("gtm_id")
    gtm_head = gtm_body = ""
    if gtm and not PREVIEW:
        gtm_head = (f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});"
                    f"var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
                    f"j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})"
                    f"(window,document,'script','dataLayer','{gtm}');</script>")
        gtm_body = (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}" height="0" width="0" '
                    f'style="display:none;visibility:hidden"></iframe></noscript>')
    u = pg.url
    nav = [("/programmy/", "Цены"), ("/#massazh", "Массаж"), ("/#spa", "SPA"), ("/mastera/", "Мастера"), ("/contact/", "Контакты")]
    nav_html = "".join(
        f'<a href="{u("/") + href[1:] if href.startswith("/#") else u(href)}">{e(label)}</a>' for href, label in nav)
    canonical = S["domain"] + pg.path
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{S['domain']}/assets/img/{image}">
<meta name="theme-color" content="#1f1712">
<link rel="icon" href="{u('/assets/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('/assets/style.css')}">
{jsonld()}
{gtm_head}
</head>
<body>
{gtm_body}
<header class="site-header">
  <div class="wrap header-row">
    <a class="logo" href="{u('/')}"><span class="logo-main">The Palm</span><span class="logo-sub">massage &amp; spa</span></a>
    <nav class="nav" id="nav">{nav_html}</nav>
    <div class="header-cta">
      <a class="header-phone" href="tel:{S['phone_href']}" data-track="phone_click" data-where="header">{e(S['phone'])}</a>
      {btn_wa("Записаться", where="header", cls="btn btn-primary btn-sm")}
      <button class="burger" aria-label="Меню" aria-controls="nav" aria-expanded="false"><span></span><span></span></button>
    </div>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <div class="logo"><span class="logo-main">The Palm</span><span class="logo-sub">massage &amp; spa</span></div>
      <p class="muted">Массаж и SPA в Алматы. {e(S['hours'])}.</p>
    </div>
    <div>
      <h3>Контакты</h3>
      <p><a href="tel:{S['phone_href']}" data-track="phone_click" data-where="footer">{e(S['phone'])}</a><br>
      <a href="{e(wa_link())}" target="_blank" rel="noopener" data-track="whatsapp_click" data-where="footer">WhatsApp</a><br>
      {e(S['address_short'])}</p>
    </div>
    <div>
      <h3>Разделы</h3>
      <p><a href="{u('/programmy/')}">Цены и программы</a><br><a href="{u('/mastera/')}">Мастера</a><br><a href="{u('/blog/')}">Блог</a><br><a href="{u('/contact/')}">Контакты</a></p>
    </div>
    <div>
      <h3>Мы в соцсетях</h3>
      <p><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram</a><br><a href="{S['tiktok']}" target="_blank" rel="noopener">TikTok</a></p>
    </div>
  </div>
  <div class="wrap footer-bottom muted">© The Palm massage &amp; spa, Алматы</div>
</footer>
<div class="mobile-bar">
  {btn_wa("WhatsApp", where="mobile_bar", cls="btn btn-primary")}
  {btn_call("Позвонить", where="mobile_bar", cls="btn btn-dark")}
</div>
<script src="{u('/assets/main.js')}" defer></script>
</body>
</html>
"""


def img(pg, name, alt, cls="", loading="lazy", w=None, h=None):
    size = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img class="{cls}" src="{pg.url("/assets/img/" + name)}" alt="{e(alt)}" loading="{loading}"{size}>'


def promos_block():
    items = "".join(f'<div class="promo"><strong>{e(p["title"])}</strong><span>{e(p["text"])}</span></div>' for p in S["promos"])
    return f'<section class="promos"><div class="wrap promos-row">{items}<p class="promo-note">{e(S["promo_note"])}</p></div></section>'


def program_card(pg, p):
    return f"""<a class="card" href="{pg.url('/programmy/' + p['slug'] + '/')}">
  {img(pg, p['image'], p['title'], 'card-img', w=1080, h=610)}
  <div class="card-body">
    <h3>{e(p['title'])}</h3>
    <p class="muted">{e(p['lead'])}</p>
    <div class="card-foot"><span class="price">от {fmt(min_price(p))}</span><span class="more">Подробнее →</span></div>
  </div>
</a>"""


def spa_card(pg, p):
    comps = "".join(f"<li>{e(c)}</li>" for c in p["components"])
    dur = p["prices"][0]["label"]
    return f"""<article class="spa-card">
  {img(pg, p['image'], p['title'], 'spa-img', w=1080, h=610)}
  <div class="spa-body">
    <h3><a href="{pg.url('/programmy/' + p['slug'] + '/')}">{e(p['title'])}</a></h3>
    <p class="spa-meta"><span class="price">{fmt(min_price(p))}</span> · {e(dur)}</p>
    <ul class="checks">{comps}</ul>
    {btn_wa("Записаться", topic=p['title'], where="spa_card", cls="btn btn-outline btn-sm")}
  </div>
</article>"""


def master_card(pg, m):
    skills = "".join(f"<li>{e(s)}</li>" for s in m["skills"])
    return f"""<article class="master">
  {img(pg, m['photo'], 'Мастер ' + m['name'], 'master-img', w=510, h=600)}
  <div class="master-body">
    <h3>{e(m['name'])}</h3>
    <p class="muted small">Опыт: {e(m['experience'])}</p>
    <p class="small">{e(m['about'])}</p>
    <ul class="tags">{skills}</ul>
    {btn_wa("Записаться к " + m['name'], topic="к мастеру " + m['name'], where="master", cls="btn btn-outline btn-sm")}
  </div>
</article>"""


def price_rows(items):
    return "".join(f'<div class="price-row"><span>{e(x["label"])}</span><span class="dots"></span><strong>{fmt(price_of(x))}</strong></div>'
                   for x in items)


def price_list(pg):
    out = []
    for key, label in GROUPS:
        progs = [p for p in PROGRAMS if p["group"] == key]
        blocks = "".join(f"""<div class="price-block">
  <h3><a href="{pg.url('/programmy/' + p['slug'] + '/')}">{e(p['title'])}</a></h3>
  {price_rows(p['prices'])}
</div>""" for p in progs)
        out.append(f'<div class="price-group"><h2>{e(label)}</h2><div class="price-grid">{blocks}</div></div>')
    rit = PROGRAMS_DATA.get("rituals") or []
    if rit:
        out.append(f"""<div class="price-group"><h2>SPA-ритуалы</h2><div class="price-grid"><div class="price-block">
  {price_rows(rit)}
  <p class="muted small">Состав ритуалов расскажет администратор в WhatsApp.</p>
</div></div></div>""")
    return "".join(out)


def faq():
    qa = [
        ("Вы правда работаете круглосуточно?", "Да, The Palm открыт 24/7, без выходных. Можно прийти после работы, поздно вечером или ранним утром."),
        ("Как записаться?", "Напишите нам в WhatsApp или позвоните по номеру " + S["phone"] + ". Администратор подберёт время и мастера."),
        ("Есть ли скидки?", "По будням с 10:00 до 17:00 скидка 10% на все программы. Для первого посещения скидка 10% на любые процедуры. Скидки не суммируются."),
        ("Что взять с собой?", "Ничего. Есть душевые, халаты, полотенца и одноразовые тапочки. Приходите налегке."),
    ]
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)
    return f'<section class="section"><div class="wrap narrow"><h2 class="h2">Частые вопросы</h2><div class="faq">{items}</div></div></section>'


def contacts_block(pg, heading="Как нас найти"):
    lat, lon = S["geo"]["lat"], S["geo"]["lon"]
    gmaps = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
    gis = f"https://2gis.kz/almaty/geo/{lon},{lat}"
    return f"""<section class="section contacts" id="kontakty">
  <div class="wrap contacts-grid">
    <div>
      <h2 class="h2">{e(heading)}</h2>
      <p class="lead">{e(S['address'])}<br><span class="muted">{e(S['address_hint'])}</span></p>
      <p><strong>{e(S['hours'])}</strong></p>
      <p><a href="tel:{S['phone_href']}" data-track="phone_click" data-where="contacts">{e(S['phone'])}</a> · <a href="mailto:{S['email']}">{e(S['email'])}</a></p>
      <div class="btn-row">{btn_wa(where="contacts")}{btn_call(where="contacts")}</div>
      <p class="route-links"><a href="{gmaps}" target="_blank" rel="noopener" data-track="route_click" data-where="google_maps">Маршрут в Google Maps</a>
      <a href="{gis}" target="_blank" rel="noopener" data-track="route_click" data-where="2gis">Открыть в 2ГИС</a></p>
    </div>
    <div class="map"><iframe title="The Palm на карте" loading="lazy" src="https://maps.google.com/maps?q={lat},{lon}&z=16&hl=ru&output=embed"></iframe></div>
  </div>
</section>"""


# ---------- страницы ----------

HOME_MASSAGE = ["klassicheskij-massazh", "stoun-massazh", "massazh-v-4-ruki", "massazh-dlya-dvoih", "sportivnyj-massazh", "ognennyj-massazh"]


def page_home():
    pg = Page("/")
    massage_cards = "".join(program_card(pg, by_slug(s)) for s in HOME_MASSAGE)
    spa_cards = "".join(spa_card(pg, p) for p in PROGRAMS if p["group"] == "spa")
    masters = "".join(master_card(pg, m) for m in MASTERS[:8])
    body = f"""
<section class="hero">
  {img(pg, 'hero.webp', 'Вход в The Palm massage & spa', 'hero-bg', loading='eager', w=1080, h=730)}
  <div class="wrap hero-inner">
    <p class="eyebrow">Массаж и SPA в Алматы · 24/7</p>
    <h1>Территория релакса в&nbsp;центре Алматы</h1>
    <p class="hero-text">Приватные кабинеты, сауна и {len(MASTERS)} мастеров. Классические и авторские массажи, SPA-программы с парением и пилингом. Работаем круглосуточно.</p>
    <div class="btn-row">{btn_wa(where="hero")}{btn_call(S['phone'], where="hero", cls="btn btn-ghost")}</div>
    <ul class="facts">
      <li><strong>24/7</strong><span>без выходных</span></li>
      <li><strong>от {fmt(min(min_price(p) for p in PROGRAMS if p['group'] == 'massage'))}</strong><span>массаж</span></li>
      <li><strong>−10%</strong><span>на первое посещение</span></li>
      <li><strong>Аль-Фараби 41/7</strong><span>ЖК Metropole</span></li>
    </ul>
  </div>
</section>
{promos_block()}
<section class="section" id="mastera">
  <div class="wrap">
    <div class="section-head"><h2 class="h2">Наши мастера</h2><a class="link" href="{pg.url('/mastera/')}">Все мастера →</a></div>
    <div class="masters">{masters}</div>
  </div>
</section>
<section class="section" id="massazh">
  <div class="wrap">
    <div class="section-head"><h2 class="h2">Популярные массажи</h2><a class="link" href="{pg.url('/programmy/')}">Все цены →</a></div>
    <div class="cards">{massage_cards}</div>
  </div>
</section>
<section class="section section-dark" id="spa">
  <div class="wrap">
    <div class="section-head"><h2 class="h2">SPA-программы</h2><p class="muted">Массаж, парение, пилинг и уход в одном визите</p></div>
    <div class="spa-grid">{spa_cards}</div>
  </div>
</section>
<section class="section comfort">
  <div class="wrap comfort-grid">
    {img(pg, 'reception.webp', 'Ресепшен The Palm', 'comfort-main', w=900, h=1373)}
    <div>
      <h2 class="h2">Комфорт в каждой детали</h2>
      <p class="lead">Приходите налегке, остальное мы подготовим.</p>
      <ul class="checks">
        <li>Приватные кабинеты с приглушённым светом</li>
        <li>Собственные душевые</li>
        <li>Мягкие халаты и полотенца, одноразовые тапочки</li>
        <li>Сауна, веники, банные шапки и масла</li>
      </ul>
      <div class="comfort-thumbs">
        {img(pg, 'wardrobe.webp', 'Гардероб с халатами', w=900, h=1406)}
        {img(pg, 'shower.webp', 'Душевая', w=1080, h=610)}
      </div>
    </div>
  </div>
</section>
{faq()}
{contacts_block(pg)}
"""
    return pg, layout(pg, "Массаж и SPA в Алматы 24/7 — The Palm massage & spa",
                      "Массаж и SPA-программы в Алматы круглосуточно. Аль-Фараби 41/7, ЖК Metropole. Цены на сайте, запись в WhatsApp. −10% на первое посещение.",
                      body, image="hero.webp")


def page_program(p):
    pg = Page(f"/programmy/{p['slug']}/")
    comps = ""
    if p["components"]:
        comps = '<h2 class="h3">Что входит</h2><ul class="checks">' + "".join(f"<li>{e(c)}</li>" for c in p["components"]) + "</ul>"
    note = f'<p class="note">{e(p["note"])}</p>' if p.get("note") else ""
    body_text = f'<p>{e(p["body"])}</p>' if p["body"] else ""
    others = [x for x in PROGRAMS if x["group"] == p["group"] and x["slug"] != p["slug"]][:3]
    other_cards = "".join(program_card(pg, x) for x in others)
    body = f"""
<section class="program-hero">
  <div class="wrap program-grid">
    <div>
      <p class="crumbs"><a href="{pg.url('/')}">Главная</a> / <a href="{pg.url('/programmy/')}">Цены</a></p>
      <h1>{e(p['title'])}</h1>
      <p class="lead">{e(p['lead'])}</p>
      <div class="price-card">{price_rows(p['prices'])}</div>
      <div class="btn-row">{btn_wa(topic=p['title'], where="program")}{btn_call(where="program")}</div>
      <p class="muted small">{e(S['promos'][0]['text'])} {e(S['promos'][1]['text'])} {e(S['promo_note'])}</p>
    </div>
    {img(pg, p['image'], p['title'], 'program-img', loading='eager', w=1080, h=610)}
  </div>
</section>
<section class="section">
  <div class="wrap narrow prose">
    {body_text}
    {comps}
    {note}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2 class="h2">Посмотрите также</h2><a class="link" href="{pg.url('/programmy/')}">Все цены →</a></div>
    <div class="cards">{other_cards}</div>
  </div>
</section>
{contacts_block(pg)}
"""
    title = f"{p.get('seo_title') or p['title']} — от {fmt(min_price(p))} | The Palm 24/7"
    desc = f"{p['title']} в The Palm massage & spa, Алматы. {p['lead']} Цена от {fmt(min_price(p))}. Работаем 24/7, запись в WhatsApp."
    return pg, layout(pg, title, desc, body, image=p["image"])


def page_prices():
    pg = Page("/programmy/")
    body = f"""
<section class="page-head"><div class="wrap">
  <h1>Цены на массаж и SPA</h1>
  <p class="lead">Актуальные цены The Palm. Нажмите на программу, чтобы узнать подробнее.</p>
  <div class="btn-row">{btn_wa(where="prices_top")}{btn_call(where="prices_top")}</div>
</div></section>
{promos_block()}
<section class="section"><div class="wrap">{price_list(pg)}</div></section>
{contacts_block(pg)}
"""
    return pg, layout(pg, "Цены на массаж и SPA в Алматы — The Palm massage & spa",
                      "Прайс The Palm: классический, стоун, спортивный массаж, массаж в 4 руки и для двоих, SPA-программы. Алматы, 24/7.", body)


def page_masters():
    pg = Page("/mastera/")
    cards = "".join(master_card(pg, m) for m in MASTERS)
    body = f"""
<section class="page-head"><div class="wrap">
  <h1>Наши мастера</h1>
  <p class="lead">Выберите мастера и напишите нам в WhatsApp, мы подберём удобное время.</p>
</div></section>
<section class="section"><div class="wrap"><div class="masters">{cards}</div></div></section>
{contacts_block(pg)}
"""
    return pg, layout(pg, "Мастера массажа — The Palm massage & spa, Алматы",
                      "Мастера массажа и SPA The Palm в Алматы: опыт, техники, запись к мастеру в WhatsApp.", body)


def page_contacts():
    pg = Page("/contact/")
    body = f"""
<section class="page-head"><div class="wrap"><h1>Контакты</h1></div></section>
{contacts_block(pg, "Адрес и часы работы")}
"""
    return pg, layout(pg, "Контакты — The Palm massage & spa, Алматы",
                      f"{S['address']}, Алматы. {S['hours']}. Телефон и WhatsApp {S['phone']}.", body)


def page_404():
    pg = Page("/404.html")
    body = f"""
<section class="page-head"><div class="wrap">
  <h1>Страница не найдена</h1>
  <p class="lead">Возможно, она переехала. Посмотрите <a href="{pg.url('/programmy/')}">цены и программы</a> или напишите нам.</p>
  <div class="btn-row">{btn_wa(where="404")}</div>
</div></section>"""
    return pg, layout(pg, "Страница не найдена — The Palm", "Страница не найдена.", body)


MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]


def ru_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def page_blog():
    pg = Page("/blog/")
    items = "".join(f"""<a class="post-item" href="{pg.url('/' + p['slug'] + '/')}">
  <span class="muted small">{ru_date(p['date'])}</span>
  <h2>{e(p['title'])}</h2>
  <p class="muted">{e(p['description'])}</p>
</a>""" for p in BLOG)
    body = f"""
<section class="page-head"><div class="wrap narrow"><h1>Блог о массаже</h1>
<p class="lead">Статьи о техниках массажа, пользе и противопоказаниях.</p></div></section>
<section class="section"><div class="wrap narrow"><div class="post-list">{items}</div></div></section>
"""
    return pg, layout(pg, "Блог о массаже — The Palm massage & spa, Алматы",
                      "Статьи о массаже: виды техник, польза, противопоказания, советы мастеров The Palm.", body)


def page_post(p):
    pg = Page(f"/{p['slug']}/")
    content = p["html"].replace("<a data-wa>", f'<a href="{e(wa_link())}" target="_blank" rel="noopener" data-track="whatsapp_click" data-where="blog_inline">')
    body = f"""
<article class="section post">
  <div class="wrap narrow">
    <p class="crumbs"><a href="{pg.url('/')}">Главная</a> / <a href="{pg.url('/blog/')}">Блог</a></p>
    <h1>{e(p['title'])}</h1>
    <p class="muted small">{ru_date(p['date'])}</p>
    <div class="prose">{content}</div>
    <div class="post-cta">
      <h2 class="h3">Записаться в The Palm</h2>
      <p>Массаж и SPA в Алматы, круглосуточно. {e(S['address_short'])}.</p>
      <div class="btn-row">{btn_wa(where="blog_post")}<a class="btn btn-outline" href="{pg.url('/programmy/')}">Цены и программы</a></div>
    </div>
  </div>
</article>
"""
    return pg, layout(pg, f"{p['title']} — блог The Palm", p["description"], body)


# ---------- сборка ----------

def write(path, content):
    full = os.path.join(DIST, path.lstrip("/"))
    if path.endswith("/"):
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    pages = [page_home(), page_prices(), page_masters(), page_contacts(), page_404()]
    pages += [page_program(p) for p in PROGRAMS]
    pages += [page_blog()] + [page_post(p) for p in BLOG]
    for pg, content in pages:
        write(pg.path, content)

    # Переадресация старых адресов WordPress (Cloudflare Pages _redirects)
    redirects = ["/elementor-6259/ /mastera/ 301", "/elementor-6259 /mastera/ 301"]
    for p in PROGRAMS:
        for old in p["old_urls"]:
            redirects.append(f"{old} /programmy/{p['slug']}/ 301")
            redirects.append(f"{old.rstrip('/')} /programmy/{p['slug']}/ 301")
    redirects += ["/product-category/* /programmy/ 301", "/shop/ /programmy/ 301"]
    # Не перенесённые статьи и старые служебные страницы WordPress
    for old in ["/body-massage/", "/spa-massage-almaty/", "/body-massage-almaty/", "/about-hotel/", "/massage-almaty/", "/refund_returns-2/"]:
        redirects.append(f"{old} / 301")
        redirects.append(f"{old.rstrip('/')} / 301")
    with open(os.path.join(DIST, "_redirects"), "w") as f:
        f.write("\n".join(redirects) + "\n")

    urls = [pg.path for pg, _ in pages if pg.path.endswith("/")]
    with open(os.path.join(DIST, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.write("".join(f"  <url><loc>{S['domain']}{u}</loc></url>\n" for u in urls))
        f.write("</urlset>\n")
    with open(os.path.join(DIST, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {S['domain']}/sitemap.xml\n")
    print(f"OK: {len(pages)} страниц в {DIST}{' (preview)' if PREVIEW else ''}")


if __name__ == "__main__":
    main()
