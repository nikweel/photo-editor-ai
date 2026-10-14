# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · **Italiano** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** è un editor di foto gratuito e open source: correzione automatica con IA, curva dei toni in stile Photoshop, HSL, pacchetti di filtri importabili ed esportabili, libreria in stile Lightroom ed elaborazione in batch. La modifica è non distruttiva e tutto funziona in locale sul tuo computer.

## Schermate

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funzionalità

- **Correzione automatica con IA:** esposizione + colore o solo esposizione, con protezione contro le alte luci bruciate; il risultato resta come normali cursori che puoi rifinire.
- **Modifica manuale:** esposizione, contrasto, alte luci e ombre, bilanciamento del bianco, curva dei toni in stile Photoshop, HSL, nitidezza, chiarezza, rimozione della foschia, vignettatura, grana.
- **Ritaglio e rotazione**, cursore **prima / dopo** trascinabile, zoom, annulla / ripeti.
- **60 filtri in 9 pacchetti:** raggruppamento per pacchetto o tipo, salvataggio dei tuoi, importazione ed esportazione di filtri singoli o interi pacchetti (`.pack.json`) e LUT `.cube`.
- **Libreria e importazione** in stile Lightroom, pellicola di miniature, valutazione a stelle, **elaborazione in batch**, esportazione in JPEG, PNG, WebP o TIFF.
- File **RAW** della maggior parte delle fotocamere (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Non distruttivo: gli originali non vengono mai modificati. Tutto gira sul tuo computer — senza cloud e senza account.

## Download (senza Python)

Scarica il `.deb` o l'`.AppImage` per Ubuntu / Debian dalla pagina [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Avvio dai sorgenti

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licenza

[MIT](LICENSE). Componenti di terze parti e pesi dei modelli: vedi [NOTICE](NOTICE).

**Documentazione completa:** [English](README.md) · [Русский](README.ru.md)
