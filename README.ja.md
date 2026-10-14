# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · **日本語** · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** は無料のオープンソース写真編集ソフトです。AI による自動補正、Photoshop 風のトーンカーブ、HSL、インポート／エクスポートできるフィルターパック、Lightroom 風のライブラリ、一括処理を備えています。編集は非破壊で、すべてお使いのコンピューター上で動作します。

## スクリーンショット

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## 機能

- **AI 自動補正：** 露出＋色、または露出のみ。ハイライトの白飛びを防ぎ、結果は通常のスライダーとして残るので微調整できます。
- **手動編集：** 露出、コントラスト、ハイライトとシャドウ、ホワイトバランス、Photoshop 風トーンカーブ、HSL、シャープ、明瞭度、霞の除去、周辺光量、粒状感。
- **切り抜きと回転**、ドラッグできる**ビフォー／アフター**スライダー、ズーム、元に戻す／やり直し。
- **9 つのパックに 60 種のフィルター：** パックまたはタイプ別にグループ化、自作フィルターの保存、単体またはパック全体（`.pack.json`）と `.cube` LUT のインポート／エクスポート。
- Lightroom 風の**ライブラリとインポート**、フィルムストリップ、星評価、**一括処理**、JPEG・PNG・WebP・TIFF への書き出し。
- ほとんどのカメラの **RAW** ファイル（CR2、CR3、NEF、ARW、DNG、ORF、RAF、RW2 など）。
- 非破壊：元のファイルは決して変更されません。すべてお使いのコンピューターで動作し、クラウドもアカウントも不要です。

## ダウンロード（Python 不要）

Ubuntu / Debian 用の `.deb` または `.AppImage` を [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) ページから入手してください：

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## ソースから実行

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## ライセンス

[MIT](LICENSE)。サードパーティ製コンポーネントとモデルの重み：[NOTICE](NOTICE) を参照。

**詳細ドキュメント:** [English](README.md) · [Русский](README.ru.md)
