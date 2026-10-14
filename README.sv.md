# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · **Svenska** · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** är en gratis fotoredigerare med öppen källkod: automatisk korrigering med AI, tonkurva som i Photoshop, HSL, filterpaket som kan importeras och exporteras, ett bibliotek som i Lightroom och batchbehandling. Redigeringen är icke-destruktiv och allt körs lokalt på din dator.

## Skärmbilder

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funktioner

- **Automatisk AI-korrigering:** exponering + färg eller bara exponering, med skydd mot utbrända högdagrar; resultatet förblir vanliga reglage som du kan finjustera.
- **Manuell redigering:** exponering, kontrast, högdagrar och skuggor, vitbalans, tonkurva som i Photoshop, HSL, skärpa, klarhet, dimborttagning, vinjettering, korn.
- **Beskärning och rotation**, ett **före / efter**-reglage som du kan dra i, zoom, ångra / gör om.
- **60 filter i 9 paket:** gruppera efter paket eller typ, spara egna, importera och exportera enskilda filter eller hela paket (`.pack.json`) och `.cube`-LUT:ar.
- **Bibliotek och import** som i Lightroom, filmremsa, stjärnbetyg, **batchbehandling**, export till JPEG, PNG, WebP eller TIFF.
- **RAW**-filer från de flesta kameror (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Icke-destruktivt: dina original ändras aldrig. Allt körs på din dator — utan moln och utan konto.

## Ladda ner (utan Python)

Hämta `.deb` eller `.AppImage` för Ubuntu / Debian från sidan [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Köra från källkod

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licens

[MIT](LICENSE). Tredjepartskomponenter och modellvikter: se [NOTICE](NOTICE).

**Fullständig dokumentation:** [English](README.md) · [Русский](README.ru.md)
