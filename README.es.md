# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · **Español** · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** es un editor de fotos gratuito y de código abierto: corrección automática con IA, curva de tonos al estilo Photoshop, HSL, paquetes de filtros importables y exportables, biblioteca al estilo Lightroom y procesamiento por lotes. La edición es no destructiva y todo funciona de forma local en tu ordenador.

## Capturas de pantalla

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Características

- **Corrección automática con IA:** exposición + color o solo exposición, con protección contra las altas luces quemadas; el resultado queda como controles deslizantes normales que puedes ajustar.
- **Edición manual:** exposición, contraste, altas luces y sombras, balance de blancos, curva de tonos al estilo Photoshop, HSL, nitidez, claridad, eliminación de neblina, viñeta, grano.
- **Recorte y rotación**, control **antes / después** que se puede arrastrar, zoom, deshacer / rehacer.
- **60 filtros en 9 paquetes:** agrupación por paquete o tipo, guarda los tuyos, importa y exporta filtros sueltos o paquetes completos (`.pack.json`) y LUT `.cube`.
- **Biblioteca e importación** al estilo Lightroom, tira de miniaturas, valoración por estrellas, **procesamiento por lotes**, exportación a JPEG, PNG, WebP o TIFF.
- Archivos **RAW** de la mayoría de las cámaras (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- No destructivo: tus originales nunca se modifican. Todo funciona en tu ordenador, sin nube y sin cuenta.

## Descarga (sin Python)

Descarga el `.deb` o el `.AppImage` para Ubuntu / Debian desde la página [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Ejecutar desde el código fuente

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licencia

[MIT](LICENSE). Componentes de terceros y pesos de modelos: consulta [NOTICE](NOTICE).

**Documentación completa:** [English](README.md) · [Русский](README.ru.md)
