# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · **Slovenčina** · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** je bezplatný fotoeditor s otvoreným zdrojovým kódom: automatická korekcia umelou inteligenciou, tónová krivka ako vo Photoshope, HSL, balíky filtrov s importom a exportom, knižnica ako v Lightroome a dávkové spracovanie. Úpravy sú nedeštruktívne a všetko beží lokálne vo vašom počítači.

## Snímky obrazovky

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funkcie

- **Automatická korekcia umelou inteligenciou:** expozícia + farba alebo len expozícia, s ochranou svetiel pred vypálením; výsledok zostane ako bežné posuvníky, ktoré môžete doladiť.
- **Ručné úpravy:** expozícia, kontrast, svetlá a tiene, vyváženie bielej, tónová krivka ako vo Photoshope, HSL, ostrosť, čistota, odstránenie hmly, vinetácia, zrno.
- **Orezanie a otočenie**, presúvateľný posuvník **pred / po**, priblíženie, späť / znova.
- **60 filtrov v 9 balíkoch:** zoskupenie podľa balíkov alebo typov, ukladanie vlastných, import a export jednotlivých filtrov alebo celých balíkov (`.pack.json`) i `.cube` LUT.
- **Knižnica a import** ako v Lightroome, pás náhľadov, hodnotenie hviezdičkami, **dávkové spracovanie**, export do JPEG, PNG, WebP alebo TIFF.
- Súbory **RAW** väčšiny fotoaparátov (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nedeštruktívne: originály sa nikdy nemenia. Všetko beží vo vašom počítači — bez cloudu a bez účtu.

## Stiahnutie (bez Pythonu)

Stiahnite `.deb` alebo `.AppImage` pre Ubuntu / Debian zo stránky [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Spustenie zo zdrojového kódu

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licencia

[MIT](LICENSE). Komponenty tretích strán a váhy modelov: pozri [NOTICE](NOTICE).

**Úplná dokumentácia:** [English](README.md) · [Русский](README.ru.md)
