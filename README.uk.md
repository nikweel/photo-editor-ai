# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · **Українська**

**Photo Editor AI** — безкоштовний фоторедактор з відкритим кодом: автоматична корекція зі штучним інтелектом, тонова крива як у Photoshop, HSL, пакети фільтрів з імпортом та експортом, бібліотека як у Lightroom і пакетна обробка. Редагування неруйнівне, а все працює локально на вашому комп'ютері.

## Знімки екрана

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Можливості

- **Автоматична корекція ШІ:** експозиція + колір або лише експозиція, із захистом світлих ділянок від пересвіту; результат залишається звичайними повзунками, які можна доналаштувати.
- **Ручне редагування:** експозиція, контраст, світла й тіні, баланс білого, тонова крива як у Photoshop, HSL, різкість, чіткість, прибирання серпанку, віньєтка, зерно.
- **Кадрування й поворот**, повзунок **до / після**, який можна перетягувати, масштабування, скасувати / повторити.
- **60 фільтрів у 9 пакетах:** групування за пакетами або типами, збереження власних, імпорт та експорт окремих фільтрів або цілих пакетів (`.pack.json`) і `.cube` LUT.
- **Бібліотека та імпорт** як у Lightroom, стрічка мініатюр, оцінки зірками, **пакетна обробка**, експорт у JPEG, PNG, WebP або TIFF.
- **RAW**-файли більшості камер (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Неруйнівно: оригінали ніколи не змінюються. Усе працює на вашому комп'ютері — без хмари й без облікового запису.

## Завантаження (без Python)

Отримайте `.deb` або `.AppImage` для Ubuntu / Debian зі сторінки [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Запуск із вихідного коду

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Ліцензія

[MIT](LICENSE). Сторонні компоненти та ваги моделей: див. [NOTICE](NOTICE).

**Повна документація:** [English](README.md) · [Русский](README.ru.md)
