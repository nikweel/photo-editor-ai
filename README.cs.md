# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · **Čeština** · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** je bezplatný fotoeditor s otevřeným kódem: automatická korekce umělou inteligencí, tónová křivka jako ve Photoshopu, HSL, balíčky filtrů s importem a exportem, knihovna jako v Lightroomu a dávkové zpracování. Úpravy jsou nedestruktivní a vše běží lokálně ve vašem počítači.

## Snímky obrazovky

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funkce

- **Automatická korekce umělou inteligencí:** expozice + barva nebo jen expozice, s ochranou světel před přepálením; výsledek zůstane jako běžné posuvníky, které můžete doladit.
- **Ruční úpravy:** expozice, kontrast, světla a stíny, vyvážení bílé, tónová křivka jako ve Photoshopu, HSL, ostrost, čirost, odstranění mlhy, vinětace, zrno.
- **Ořez a otočení**, přetahovatelný posuvník **před / po**, zvětšení, zpět / znovu.
- **60 filtrů v 9 balíčcích:** seskupení podle balíčků nebo typů, ukládání vlastních, import a export jednotlivých filtrů nebo celých balíčků (`.pack.json`) i `.cube` LUT.
- **Knihovna a import** jako v Lightroomu, pás náhledů, hodnocení hvězdičkami, **dávkové zpracování**, export do JPEG, PNG, WebP nebo TIFF.
- Soubory **RAW** většiny fotoaparátů (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nedestruktivní: originály se nikdy nemění. Vše běží ve vašem počítači — bez cloudu a bez účtu.

## Stažení (bez Pythonu)

Stáhněte `.deb` nebo `.AppImage` pro Ubuntu / Debian ze stránky [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Spuštění ze zdrojového kódu

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licence

[MIT](LICENSE). Komponenty třetích stran a váhy modelů: viz [NOTICE](NOTICE).

**Úplná dokumentace:** [English](README.md) · [Русский](README.ru.md)
