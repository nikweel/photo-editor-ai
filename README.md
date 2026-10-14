# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · **English** · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** is a free, open-source desktop photo editor with **AI auto-correction**, a Photoshop-style tone curve, HSL, filter **packs** you can import and export, a Lightroom-style library and batch processing.
It edits **non-destructively**: your originals are never modified — all edits are stored as settings and applied on export.

> 🖥️ **Linux, Windows and macOS.** Built with Python, PySide6 (Qt) and ONNX Runtime. Everything runs **locally**: no cloud, no account.

## Screenshots
*(demo with a generated landscape)*

![Main window](docs/screenshots/main.png)
![Before / After slider with a filter](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments and tone curve](docs/screenshots/manual.png)

## AI auto-correction
Two buttons on the **Auto · AI** tab: **exposure + colour** or **exposure only**, with a *strength* slider.
- The result is a set of ordinary sliders (exposure, white balance, vibrance), so you can fine-tune it by hand afterwards.
- It does not just paste a network's output: the AI estimate is averaged with a histogram analysis and **capped so highlights do not blow out**.
- **Models** (the first one is built in, the others are downloaded on demand with a SHA-256 check):

  | Model | Size | What it is for |
  |---|---|---|
  | **Built-in (histogram)** | — | No neural network, always works |
  | **IAT — exposure** | 0.5 MB | Fixes over- and under-exposure (default when installed) |
  | **IAT — low light** | 0.5 MB | Dark shots; brightens more aggressively |
  | **Your own ONNX model** | — | *Add your own…* detects the kind automatically (EV regressor or image→image) and validates it with a test run |

  The IAT models are the official [Illumination-Adaptive Transformer](https://github.com/cuiziteng/Illumination-Adaptive-Transformer) weights (Apache 2.0) converted to ONNX — see [NOTICE](NOTICE) and `scripts/export_iat.py`.

## Manual adjustments
- **Light:** exposure, contrast, highlights, shadows, whites, blacks. **Colour:** temperature, tint, vibrance, saturation.
- **Tone curve like in Photoshop:** click anywhere on the curve to add a point and drag it; `Ctrl`+click or `Delete` removes it; arrow keys nudge; black/white points move; RGB / R / G / B channels, presets and a histogram behind the curve.
- **HSL** for 8 colours (hue, saturation, luminance), **detail** (sharpness, texture, clarity, colour noise) and **effects** (dehaze, vignette, grain).
- **Crop and rotate:** interactive crop with aspect ratios, 90° rotation, flips, horizon straightening.
- **Handy controls:** click a number next to a slider to type the exact value; every section has a reset button and a dot that shows it has changes; hover a slider for a hint; `J` shows blown highlights (red) and crushed shadows (blue) on the photo.
- **Before / After** slider you can drag, zoom with the mouse wheel, a live histogram, **undo / redo** (`Ctrl+Z`).
- Smooth even with heavy filters: a fast draft while you drag, the full-quality render follows in the background.
- **RAW** files (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2, PEF and more) through rawpy / LibRaw.

## Filters and packs
**60 built-in filters in 9 packs**: Basic, Portrait, Landscape, Street & City, Film & Vintage, Black & White, Food, Dark & Moody, and looks tuned numerically from before/after pairs.
- **Group** by *packs*, by *type* (Portrait, Landscape, B&W, Cinema, Film, …) or as a flat list; **search** by name, pack or type.
- A **strength** slider mixes the filter with the original.
- **Save your own** filter into your own pack (a new pack is created on the fly) with a type of your choice.
- **Share:** export one filter or a **whole pack** as a single `.pack.json`; *Import…* adds filters, packs and `.cube` LUTs. Imported files are validated and LUT paths from untrusted files are ignored.
- Filters never touch your crop and rotation.

<details><summary>Pack file format</summary>

```json
{ "format": "photo-editor-ai-pack", "version": 1, "name": "My pack", "description": "…",
  "filters": [ { "name": "Warm", "category": "Portrait", "params": { "temperature": 0.2, "contrast": 0.1 } } ] }
```
A single filter uses `"format": "photo-editor-ai-filter"` with `name`, `category`, `params`. Parameters not listed keep their default values.
</details>

## Library, import and export
- **Import like in Lightroom:** pick files or a folder, tick thumbnails, then *add in place* or *copy* (optionally into per-date folders from EXIF). Drag and drop works too.
- A **filmstrip** under the photo, **star ratings** (`0`–`5`), remove from catalog (`Delete`, the file stays), copy / paste settings between photos, apply to all.
- **Export:** JPEG, PNG, WebP, TIFF; quality, resize by the long side, keep EXIF.
- **Batch processing:** apply AI auto-correction and/or the settings of the open photo to a whole folder, with format, size and EXIF options. A broken file never stops the batch.

## Keyboard
`Ctrl+I` import · `Ctrl+U` AI auto-correction · `F` focus mode (hide panels) · `J` clipping warning · `Ctrl+S` export · `Ctrl+Z` / `Ctrl+Shift+Z` undo / redo · `\` before/after · mouse wheel zoom · `Ctrl+0` / `Ctrl+1` fit / 100% · `Alt+←/→` previous/next photo · `0`–`5` rating · `Ctrl+Shift+C/V` copy/paste settings · `Enter` / `Esc` apply/cancel crop · `F1` help.

## Download (no Python needed)
Get the file for your system from the [**Releases**](https://github.com/nikweel/photo-editor-ai/releases/latest) page:

| System | File |
|---|---|
| **Ubuntu / Debian** | `.deb` — `sudo apt install ./Photo-Editor-AI-<version>-amd64.deb` · or `.AppImage` — `chmod +x Photo-Editor-AI-*.AppImage && ./Photo-Editor-AI-*.AppImage` |
| **Windows 10/11** | `Photo-Editor-AI-<version>-Setup.exe` |
| **macOS** (Apple silicon) | `Photo-Editor-AI-<version>-macos-arm64.dmg` |
| **macOS** (Intel) | `Photo-Editor-AI-<version>-macos-intel.dmg` |

Checksums are published as `SHA256SUMS.txt`. The app keeps its catalog, filters and models in your user data folder (`~/.local/share/Photo-Editor-AI/` on Linux, `%LOCALAPPDATA%\Photo-Editor-AI\` on Windows, `~/Library/Application Support/Photo-Editor-AI/` on macOS).

> ⚠️ **The builds are not code-signed yet**, so Windows SmartScreen or macOS Gatekeeper may warn about an unknown publisher (macOS: right-click the app → *Open*). All builds are produced and smoke-tested by CI on real Windows, macOS and Linux machines (tests, start-up of the engine, Qt and ONNX Runtime), but the interface has had the most hands-on testing on Ubuntu — please report problems in [Issues](https://github.com/nikweel/photo-editor-ai/issues).
> On Windows the AI uses the GPU through DirectML when one is available and falls back to the CPU automatically.

## Run from source (Ubuntu)
You need [uv](https://docs.astral.sh/uv/) (it installs Python for you).
```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main            # or: uv run python -m app.main photo.jpg
```
- Everything is stored next to the project (portable): the catalog and your filters in `data/`, models in `models/`.
- On the first *Auto* click the app offers to download the selected AI model (0.5 MB) from the [Releases](https://github.com/nikweel/photo-editor-ai/releases) page.
- If Qt cannot start on X11, install `libxcb-cursor0` (`sudo apt install libxcb-cursor0`).

## Development
```bash
uv sync --group dev
uv run pytest -q
QT_QPA_PLATFORM=offscreen uv run python scripts/make_screenshots.py   # regenerate the screenshots
```
Layout: `app/core` (image engine: curves, HSL, mixer, details, geometry, LUT) · `app/ai` (models and auto-correction) · `app/services` (library, filters and packs, batch, export) · `app/gui` (Qt interface) · `scripts` (model export, screenshots, filter fitting).

## Roadmap
Code signing, local adjustments (masks and brushes), a channel-mixer panel, more AI models, more interface languages.

## License
[MIT](LICENSE). Third-party components and the IAT model weights: see [NOTICE](NOTICE).
