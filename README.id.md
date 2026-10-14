# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · **Bahasa Indonesia** · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** adalah editor foto gratis dan sumber terbuka: koreksi otomatis dengan AI, kurva nada ala Photoshop, HSL, paket filter yang dapat diimpor dan diekspor, pustaka ala Lightroom, dan pemrosesan massal. Pengeditan bersifat non-destruktif dan semuanya berjalan secara lokal di komputer Anda.

## Tangkapan layar

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Fitur

- **Koreksi otomatis AI:** eksposur + warna atau hanya eksposur, dengan perlindungan agar sorotan tidak terbakar; hasilnya tetap berupa penggeser biasa yang bisa Anda sesuaikan.
- **Pengeditan manual:** eksposur, kontras, sorotan dan bayangan, white balance, kurva nada ala Photoshop, HSL, ketajaman, kejernihan, penghilang kabut, vinyet, grain.
- **Pangkas dan putar**, penggeser **sebelum / sesudah** yang bisa diseret, zoom, urungkan / ulangi.
- **60 filter dalam 9 paket:** kelompokkan menurut paket atau jenis, simpan filter Anda sendiri, impor dan ekspor filter tunggal atau paket utuh (`.pack.json`) serta LUT `.cube`.
- **Pustaka dan impor** ala Lightroom, filmstrip, peringkat bintang, **pemrosesan massal**, ekspor ke JPEG, PNG, WebP, atau TIFF.
- File **RAW** dari sebagian besar kamera (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Non-destruktif: file asli Anda tidak pernah diubah. Semuanya berjalan di komputer Anda — tanpa cloud, tanpa akun.

## Unduh (tanpa Python)

Ambil `.deb` atau `.AppImage` untuk Ubuntu / Debian dari halaman [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Jalankan dari kode sumber

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Lisensi

[MIT](LICENSE). Komponen pihak ketiga dan bobot model: lihat [NOTICE](NOTICE).

**Dokumentasi lengkap:** [English](README.md) · [Русский](README.ru.md)
