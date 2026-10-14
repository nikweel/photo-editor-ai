# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · **Norsk** · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** er et gratis fotoredigeringsprogram med åpen kildekode: automatisk korrigering med KI, tonekurve som i Photoshop, HSL, filterpakker som kan importeres og eksporteres, et bibliotek som i Lightroom og batchbehandling. Redigeringen er ikke-destruktiv, og alt kjører lokalt på datamaskinen din.

## Skjermbilder

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funksjoner

- **Automatisk KI-korrigering:** eksponering + farge eller bare eksponering, med beskyttelse mot utbrente høylys; resultatet forblir vanlige glidere du kan finjustere.
- **Manuell redigering:** eksponering, kontrast, høylys og skygger, hvitbalanse, tonekurve som i Photoshop, HSL, skarphet, klarhet, fjerning av dis, vignettering, korn.
- **Beskjæring og rotering**, en **før / etter**-glider du kan dra i, zoom, angre / gjør om.
- **60 filtre i 9 pakker:** grupper etter pakke eller type, lagre dine egne, importer og eksporter enkeltfiltre eller hele pakker (`.pack.json`) og `.cube`-LUT-er.
- **Bibliotek og import** som i Lightroom, filmstrimmel, stjernevurdering, **batchbehandling**, eksport til JPEG, PNG, WebP eller TIFF.
- **RAW**-filer fra de fleste kameraer (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Ikke-destruktivt: originalene endres aldri. Alt kjører på datamaskinen din — uten sky og uten konto.

## Last ned (uten Python)

Hent `.deb` eller `.AppImage` for Ubuntu / Debian fra siden [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Kjør fra kildekode

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Lisens

[MIT](LICENSE). Tredjepartskomponenter og modellvekter: se [NOTICE](NOTICE).

**Full dokumentasjon:** [English](README.md) · [Русский](README.ru.md)
