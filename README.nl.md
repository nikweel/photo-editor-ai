# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · **Nederlands** · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** is een gratis, opensource fotobewerker: automatische AI-correctie, toonkromme zoals in Photoshop, HSL, filterpakketten met import en export, een bibliotheek zoals in Lightroom en batchverwerking. Bewerken is niet-destructief en alles draait lokaal op je computer.

## Schermafbeeldingen

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Functies

- **Automatische AI-correctie:** belichting + kleur of alleen belichting, met bescherming tegen uitgebrande hooglichten; het resultaat blijft gewone schuifregelaars die je kunt bijstellen.
- **Handmatig bewerken:** belichting, contrast, hooglichten en schaduwen, witbalans, toonkromme zoals in Photoshop, HSL, scherpte, helderheid, nevel verwijderen, vignet, korrel.
- **Bijsnijden en roteren**, een versleepbare **voor / na**-schuifregelaar, zoomen, ongedaan maken / opnieuw.
- **60 filters in 9 pakketten:** groeperen per pakket of type, eigen filters opslaan, losse filters of hele pakketten (`.pack.json`) en `.cube`-LUT's importeren en exporteren.
- **Bibliotheek en import** zoals in Lightroom, filmstrip, sterrenbeoordeling, **batchverwerking**, export naar JPEG, PNG, WebP of TIFF.
- **RAW**-bestanden van de meeste camera's (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Niet-destructief: je originelen worden nooit gewijzigd. Alles draait op je computer — geen cloud, geen account.

## Downloaden (zonder Python)

Download de `.deb` of `.AppImage` voor Ubuntu / Debian van de pagina [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Starten vanuit de broncode

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licentie

[MIT](LICENSE). Componenten van derden en modelgewichten: zie [NOTICE](NOTICE).

**Volledige documentatie:** [English](README.md) · [Русский](README.ru.md)
