# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · **中文（简体）** · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** 是一款免费开源的桌面照片编辑器：AI 自动校正、Photoshop 风格的色调曲线、HSL、可导入导出的滤镜包、类似 Lightroom 的图库与批量处理。编辑为非破坏性，所有操作都在本机完成。

## 截图

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## 功能

- **AI 自动校正：** 曝光 + 色彩，或仅曝光，并防止高光过曝；结果保留为普通滑块，可继续微调。
- **手动编辑：** 曝光、对比度、高光与阴影、白平衡、Photoshop 风格色调曲线、HSL、锐度、清晰度、去雾、暗角、颗粒。
- **裁剪与旋转**、可拖动的**前后对比**滑块、缩放、撤销 / 重做。
- **9 个包中的 60 款滤镜：** 按包或类型分组，保存自己的滤镜，导入导出单个滤镜或整个包（`.pack.json`）以及 `.cube` LUT。
- 类似 Lightroom 的**图库与导入**、胶片条、星级评分、**批量处理**，可导出为 JPEG、PNG、WebP 或 TIFF。
- 支持大多数相机的 **RAW** 文件（CR2、CR3、NEF、ARW、DNG、ORF、RAF、RW2 等）。
- 非破坏性：永不修改原始文件。一切在你的电脑上运行——无需云端，无需账号。

## 下载（无需 Python）

从 [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) 页面下载适用于 Ubuntu / Debian 的 `.deb` 或 `.AppImage`：

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## 从源码运行

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## 许可证

[MIT](LICENSE)。第三方组件与 AI 模型权重：见 [NOTICE](NOTICE)。

**完整文档:** [English](README.md) · [Русский](README.ru.md)
