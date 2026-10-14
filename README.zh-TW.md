# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · **繁體中文** · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** 是一款免費開源的桌面相片編輯器：AI 自動校正、Photoshop 風格的色調曲線、HSL、可匯入匯出的濾鏡包、類似 Lightroom 的圖庫與批次處理。編輯為非破壞性，所有運算都在本機完成。

## 螢幕截圖

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## 功能

- **AI 自動校正：** 曝光 + 色彩，或僅曝光，並避免高光過曝；結果保留為一般滑桿，可再微調。
- **手動編輯：** 曝光、對比、高光與陰影、白平衡、Photoshop 風格色調曲線、HSL、銳利度、清晰度、去霧、暈影、顆粒。
- **裁切與旋轉**、可拖曳的**前後對照**滑桿、縮放、復原 / 重做。
- **9 個包中的 60 款濾鏡：** 依包或類型分組，儲存自己的濾鏡，匯入匯出單一濾鏡或整個包（`.pack.json`）以及 `.cube` LUT。
- 類似 Lightroom 的**圖庫與匯入**、底片條、星級評分、**批次處理**，可匯出為 JPEG、PNG、WebP 或 TIFF。
- 支援多數相機的 **RAW** 檔案（CR2、CR3、NEF、ARW、DNG、ORF、RAF、RW2 等）。
- 非破壞性：絕不更動原始檔案。一切在你的電腦上執行——不需雲端，不需帳號。

## 下載（不需要 Python）

從 [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) 頁面下載適用於 Ubuntu / Debian 的 `.deb` 或 `.AppImage`：

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## 從原始碼執行

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## 授權

[MIT](LICENSE)。第三方元件與 AI 模型權重：見 [NOTICE](NOTICE)。

**完整文件:** [English](README.md) · [Русский](README.ru.md)
