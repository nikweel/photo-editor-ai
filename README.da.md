# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · **Dansk** · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** er en gratis fotoeditor med åben kildekode: automatisk korrektion med AI, tonekurve som i Photoshop, HSL, filterpakker med import og eksport, et bibliotek som i Lightroom og batchbehandling. Redigeringen er ikke-destruktiv, og alt kører lokalt på din computer.

## Skærmbilleder

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funktioner

- **Automatisk AI-korrektion:** eksponering + farve eller kun eksponering, med beskyttelse mod udbrændte højlys; resultatet forbliver almindelige skydere, du kan finjustere.
- **Manuel redigering:** eksponering, kontrast, højlys og skygger, hvidbalance, tonekurve som i Photoshop, HSL, skarphed, klarhed, fjernelse af dis, vignettering, korn.
- **Beskæring og rotation**, en **før / efter**-skyder du kan trække i, zoom, fortryd / gentag.
- **60 filtre i 9 pakker:** gruppér efter pakke eller type, gem dine egne, importér og eksportér enkelte filtre eller hele pakker (`.pack.json`) og `.cube` LUT'er.
- **Bibliotek og import** som i Lightroom, filmstrimmel, stjernebedømmelse, **batchbehandling**, eksport til JPEG, PNG, WebP eller TIFF.
- **RAW**-filer fra de fleste kameraer (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Ikke-destruktivt: dine originaler ændres aldrig. Alt kører på din computer — uden sky og uden konto.

## Download (uden Python)

Hent `.deb` eller `.AppImage` til Ubuntu / Debian fra siden [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Kør fra kildekode

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licens

[MIT](LICENSE). Tredjepartskomponenter og modelvægte: se [NOTICE](NOTICE).

**Fuld dokumentation:** [English](README.md) · [Русский](README.ru.md)
