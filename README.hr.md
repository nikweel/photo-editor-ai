# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · **Hrvatski** · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** je besplatan uređivač fotografija otvorenog koda: automatska korekcija umjetnom inteligencijom, tonska krivulja poput Photoshopa, HSL, paketi filtera s uvozom i izvozom, biblioteka poput Lightrooma i grupna obrada. Uređivanje je nedestruktivno, a sve radi lokalno na vašem računalu.

## Snimke zaslona

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Mogućnosti

- **Automatska korekcija umjetnom inteligencijom:** ekspozicija + boja ili samo ekspozicija, uz zaštitu svjetlina od izgaranja; rezultat ostaje kao obični klizači koje možete fino podesiti.
- **Ručno uređivanje:** ekspozicija, kontrast, svjetla i sjene, ravnoteža bijele, tonska krivulja poput Photoshopa, HSL, oštrina, jasnoća, uklanjanje izmaglice, vinjeta, zrnatost.
- **Obrezivanje i rotacija**, klizač **prije / poslije** koji možete povlačiti, zumiranje, poništi / ponovi.
- **60 filtera u 9 paketa:** grupiranje po paketima ili vrstama, spremanje vlastitih, uvoz i izvoz pojedinačnih filtera ili cijelih paketa (`.pack.json`) i `.cube` LUT-ova.
- **Biblioteka i uvoz** poput Lightrooma, traka sa slikama, ocjene zvjezdicama, **grupna obrada**, izvoz u JPEG, PNG, WebP ili TIFF.
- **RAW** datoteke većine fotoaparata (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nedestruktivno: originali se nikada ne mijenjaju. Sve radi na vašem računalu — bez oblaka i bez računa.

## Preuzimanje (bez Pythona)

Preuzmite `.deb` ili `.AppImage` za Ubuntu / Debian sa stranice [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Pokretanje iz izvornog koda

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licenca

[MIT](LICENSE). Komponente trećih strana i težine modela: vidi [NOTICE](NOTICE).

**Cjelovita dokumentacija:** [English](README.md) · [Русский](README.ru.md)
