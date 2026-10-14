# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · **Français** · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** est un éditeur de photos gratuit et open source : correction automatique par IA, courbe des tonalités façon Photoshop, TSL (HSL), packs de filtres importables et exportables, bibliothèque façon Lightroom et traitement par lot. Les retouches sont non destructives et tout s'exécute en local sur votre ordinateur.

## Captures d'écran

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Fonctionnalités

- **Correction automatique par IA :** exposition + couleur ou exposition seule, avec protection contre les hautes lumières brûlées ; le résultat reste de simples curseurs que vous pouvez affiner.
- **Retouche manuelle :** exposition, contraste, hautes lumières et ombres, balance des blancs, courbe des tonalités façon Photoshop, HSL, netteté, clarté, correction de la brume, vignettage, grain.
- **Recadrage et rotation**, curseur **avant / après** déplaçable, zoom, annuler / rétablir.
- **60 filtres en 9 packs :** regroupement par pack ou par type, enregistrement des vôtres, import et export de filtres seuls ou de packs entiers (`.pack.json`) et de LUT `.cube`.
- **Bibliothèque et import** façon Lightroom, bande de vignettes, notes par étoiles, **traitement par lot**, export en JPEG, PNG, WebP ou TIFF.
- Fichiers **RAW** de la plupart des appareils (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Non destructif : vos originaux ne sont jamais modifiés. Tout fonctionne sur votre ordinateur — sans cloud ni compte.

## Téléchargement (sans Python)

Récupérez le `.deb` ou l'`.AppImage` pour Ubuntu / Debian sur la page [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) :

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Lancer depuis les sources

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licence

[MIT](LICENSE). Composants tiers et poids des modèles : voir [NOTICE](NOTICE).

**Documentation complète:** [English](README.md) · [Русский](README.ru.md)
