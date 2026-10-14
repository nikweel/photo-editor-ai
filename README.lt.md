# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Lietuvių** · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** yra nemokama atvirojo kodo nuotraukų rengyklė: automatinis taisymas dirbtiniu intelektu, „Photoshop“ tipo tonų kreivė, HSL, importuojami ir eksportuojami filtrų paketai, „Lightroom“ tipo biblioteka ir paketinis apdorojimas. Redagavimas nedestruktyvus, o viskas veikia vietoje jūsų kompiuteryje.

## Ekrano nuotraukos

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Galimybės

- **Automatinis taisymas DI:** ekspozicija + spalva arba tik ekspozicija, apsaugant šviesas nuo perdegimo; rezultatas lieka kaip įprasti slankikliai, kuriuos galite tikslinti.
- **Rankinis redagavimas:** ekspozicija, kontrastas, šviesos ir šešėliai, baltos spalvos balansas, „Photoshop“ tipo tonų kreivė, HSL, ryškumas, aiškumas, ūko šalinimas, vinjetė, grūdėtumas.
- **Apkarpymas ir pasukimas**, tempiamas **prieš / po** slankiklis, mastelis, atšaukti / kartoti.
- **60 filtrų 9 paketuose:** grupavimas pagal paketus ar tipus, savų filtrų saugojimas, pavienių filtrų ar visų paketų (`.pack.json`) ir `.cube` LUT importas bei eksportas.
- **Biblioteka ir importas** kaip „Lightroom“, filmo juosta, vertinimas žvaigždutėmis, **paketinis apdorojimas**, eksportas į JPEG, PNG, WebP ar TIFF.
- Daugumos fotoaparatų **RAW** failai (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nedestruktyvu: originalai niekada nekeičiami. Viskas veikia jūsų kompiuteryje — be debesies ir be paskyros.

## Atsisiuntimas (be Python)

Atsisiųskite `.deb` arba `.AppImage` skirtą „Ubuntu“ / „Debian“ iš [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) puslapio:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Paleidimas iš šaltinio kodo

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licencija

[MIT](LICENSE). Trečiųjų šalių komponentai ir modelių svoriai: žr. [NOTICE](NOTICE).

**Išsami dokumentacija:** [English](README.md) · [Русский](README.ru.md)
