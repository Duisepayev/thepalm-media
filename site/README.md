# Сайт thepalm.kz

Статический сайт The Palm massage & spa. Собирается скриптом `build.py` (только стандартный Python) из файлов в `data/`.

## Как устроено

- `data/settings.json` — телефон, WhatsApp, адрес, акции, GTM.
- `data/altegio-services.json` — снимок услуг и цен из Altegio (location 1352802). Цены на сайте берутся только отсюда по `altegio_id`.
- `data/programs.json` — страницы программ: тексты, картинки, какие услуги Altegio показывать, старые адреса для переадресации.
- `data/masters.json` — мастера, которые работают (сверять с Altegio).
- `assets/` — стили, скрипт, картинки.

## Сборка

```
python3 build.py            # в dist/, для хостинга
python3 build.py --preview  # ссылки на index.html, для просмотра без сервера
```

Cloudflare Pages: root directory `site`, build command `python3 build.py`, output `dist`.

## Как обновить

- Цены: выгрузить услуги из Altegio в `data/altegio-services.json`, пересобрать. Сборка падает, если услуга с `altegio_id` пропала или выключена.
- Мастер: добавить/убрать в `data/masters.json`, фото 510×600 в `assets/img/master-<slug>.webp`.
- Кнопки WhatsApp начинаются с текста «Здравствуйте, пишу с сайта thepalm.kz.» — по нему бот считает заявки с сайта, не менять.

## До переключения домена

- Перенести статьи блога (/blog/) из WordPress, сохранив адреса.
- Проверить, что события `whatsapp_click`, `phone_click` в GTM настроены как конверсии Google Ads.
