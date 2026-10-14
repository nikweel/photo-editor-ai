# Photo Editor AI

[العربية](README.ar.md) · **Български** · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** е безплатен редактор за снимки с отворен код: автоматична корекция с изкуствен интелект, тонална крива като във Photoshop, HSL, пакети филтри с внос и износ, библиотека като в Lightroom и пакетна обработка. Редакциите са неразрушаващи, а всичко работи локално на вашия компютър.

## Екранни снимки

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Възможности

- **Автоматична корекция с ИИ:** експозиция + цвят или само експозиция, със защита на светлините от прегаряне; резултатът остава като обикновени плъзгачи, които можете да донастроите.
- **Ръчна обработка:** експозиция, контраст, светлини и сенки, баланс на бялото, тонална крива като във Photoshop, HSL, рязкост, яснота, премахване на мъгла, виньетка, зърно.
- **Изрязване и завъртане**, плъзгач **преди / след**, мащабиране, отмяна / повторение.
- **60 филтъра в 9 пакета:** групиране по пакети или типове, запазване на собствени, внос и износ на отделни филтри или цели пакети (`.pack.json`) и `.cube` LUT.
- **Библиотека и внос** като в Lightroom, лента със снимки, оценка със звезди, **пакетна обработка**, износ в JPEG, PNG, WebP или TIFF.
- **RAW** файлове на повечето фотоапарати (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Неразрушаващо: оригиналите никога не се променят. Всичко работи на вашия компютър — без облак и без акаунт.

## Изтегляне (без Python)

Вземете `.deb` или `.AppImage` за Ubuntu / Debian от страницата [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Стартиране от изходния код

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Лиценз

[MIT](LICENSE). Външни компоненти и тегла на моделите: виж [NOTICE](NOTICE).

**Пълна документация:** [English](README.md) · [Русский](README.ru.md)
