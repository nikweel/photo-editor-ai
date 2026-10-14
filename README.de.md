# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · **Deutsch** · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** ist ein kostenloser Open-Source-Fotoeditor: automatische KI-Korrektur, Tonwertkurve wie in Photoshop, HSL, importierbare und exportierbare Filterpakete, eine Bibliothek wie in Lightroom und Stapelverarbeitung. Die Bearbeitung ist nicht-destruktiv und alles läuft lokal auf Ihrem Rechner.

## Screenshots

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funktionen

- **Automatische KI-Korrektur:** Belichtung + Farbe oder nur Belichtung, mit Schutz vor ausgebrannten Lichtern; das Ergebnis bleibt als normale Regler erhalten, die Sie nachjustieren können.
- **Manuelle Bearbeitung:** Belichtung, Kontrast, Lichter und Tiefen, Weißabgleich, Tonwertkurve wie in Photoshop, HSL, Schärfe, Klarheit, Dunstentfernung, Vignette, Korn.
- **Zuschneiden und Drehen**, ziehbarer **Vorher / Nachher**-Regler, Zoom, Rückgängig / Wiederholen.
- **60 Filter in 9 Paketen:** Gruppierung nach Paketen oder Typen, eigene Filter speichern, einzelne Filter oder ganze Pakete (`.pack.json`) sowie `.cube`-LUTs importieren und exportieren.
- **Bibliothek und Import** wie in Lightroom, Filmstreifen, Sternebewertung, **Stapelverarbeitung**, Export als JPEG, PNG, WebP oder TIFF.
- **RAW**-Dateien der meisten Kameras (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nicht-destruktiv: Ihre Originale werden nie verändert. Alles läuft auf Ihrem Rechner — ohne Cloud und ohne Konto.

## Download (ohne Python)

Laden Sie die `.deb`- oder `.AppImage`-Datei für Ubuntu / Debian von der Seite [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) herunter:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Aus dem Quellcode starten

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Lizenz

[MIT](LICENSE). Komponenten von Drittanbietern und Modellgewichte: siehe [NOTICE](NOTICE).

**Vollständige Dokumentation:** [English](README.md) · [Русский](README.ru.md)
