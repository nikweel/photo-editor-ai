# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · **Magyar** · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

A **Photo Editor AI** ingyenes, nyílt forráskódú fotószerkesztő: automatikus MI-korrekció, Photoshop-szerű tónusgörbe, HSL, importálható és exportálható szűrőcsomagok, Lightroom-szerű könyvtár és kötegelt feldolgozás. A szerkesztés roncsolásmentes, és minden helyben, a számítógépén fut.

## Képernyőképek

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funkciók

- **Automatikus MI-korrekció:** expozíció + szín vagy csak expozíció, a kiégett fények elleni védelemmel; az eredmény hagyományos csúszkák maradnak, amelyeket finomhangolhat.
- **Kézi szerkesztés:** expozíció, kontraszt, fények és árnyékok, fehéregyensúly, Photoshop-szerű tónusgörbe, HSL, élesség, tisztaság, ködeltávolítás, vignetta, szemcse.
- **Vágás és forgatás**, húzható **előtte / utána** csúszka, nagyítás, visszavonás / ismétlés.
- **60 szűrő 9 csomagban:** csoportosítás csomagok vagy típusok szerint, saját szűrők mentése, egyes szűrők vagy teljes csomagok (`.pack.json`) és `.cube` LUT-ok importálása és exportálása.
- Lightroom-szerű **könyvtár és importálás**, filmszalag, csillagos értékelés, **kötegelt feldolgozás**, exportálás JPEG, PNG, WebP vagy TIFF formátumba.
- A legtöbb fényképezőgép **RAW** fájljai (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Roncsolásmentes: az eredeti fájlok sosem módosulnak. Minden a számítógépén fut — felhő és fiók nélkül.

## Letöltés (Python nélkül)

Töltse le a `.deb` vagy `.AppImage` fájlt Ubuntuhoz / Debianhoz a [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) oldalról:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Futtatás forráskódból

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licenc

[MIT](LICENSE). Harmadik felek összetevői és a modellsúlyok: lásd [NOTICE](NOTICE).

**Teljes dokumentáció:** [English](README.md) · [Русский](README.ru.md)
