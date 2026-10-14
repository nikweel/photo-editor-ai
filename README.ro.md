# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · **Română** · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** este un editor foto gratuit și open source: corecție automată cu IA, curbă de tonuri ca în Photoshop, HSL, pachete de filtre care se pot importa și exporta, bibliotecă ca în Lightroom și procesare în lot. Editarea este nedestructivă, iar totul rulează local pe calculatorul tău.

## Capturi de ecran

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funcții

- **Corecție automată cu IA:** expunere + culoare sau doar expunere, cu protecție împotriva luminilor arse; rezultatul rămâne sub formă de glisoare obișnuite pe care le poți ajusta.
- **Editare manuală:** expunere, contrast, lumini și umbre, balans de alb, curbă de tonuri ca în Photoshop, HSL, claritate, definiție, eliminarea ceții, vignetă, granulație.
- **Decupare și rotire**, glisor **înainte / după** care poate fi tras, zoom, anulare / refacere.
- **60 de filtre în 9 pachete:** grupare după pachet sau tip, salvarea propriilor filtre, import și export de filtre individuale sau pachete întregi (`.pack.json`) și LUT-uri `.cube`.
- **Bibliotecă și import** ca în Lightroom, bandă de miniaturi, evaluare cu stele, **procesare în lot**, export în JPEG, PNG, WebP sau TIFF.
- Fișiere **RAW** de la majoritatea aparatelor (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nedestructiv: originalele nu sunt modificate niciodată. Totul rulează pe calculatorul tău — fără cloud și fără cont.

## Descărcare (fără Python)

Descarcă `.deb` sau `.AppImage` pentru Ubuntu / Debian de pe pagina [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Rulare din codul sursă

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licență

[MIT](LICENSE). Componente terțe și ponderile modelelor: vezi [NOTICE](NOTICE).

**Documentație completă:** [English](README.md) · [Русский](README.ru.md)
