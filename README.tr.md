# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · **Türkçe** · [Українська](README.uk.md)

**Photo Editor AI**, ücretsiz ve açık kaynaklı bir fotoğraf düzenleyicidir: yapay zekâ ile otomatik düzeltme, Photoshop tarzı ton eğrisi, HSL, içe ve dışa aktarılabilen filtre paketleri, Lightroom tarzı kütüphane ve toplu işleme. Düzenleme yıkıcı değildir ve her şey bilgisayarınızda yerel olarak çalışır.

## Ekran görüntüleri

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Özellikler

- **Yapay zekâ ile otomatik düzeltme:** pozlama + renk ya da yalnızca pozlama; parlak alanların yanmasına karşı korumayla. Sonuç, ince ayar yapabileceğiniz normal kaydırıcılar olarak kalır.
- **Elle düzenleme:** pozlama, kontrast, parlak alanlar ve gölgeler, beyaz dengesi, Photoshop tarzı ton eğrisi, HSL, keskinlik, netlik, sis giderme, vinyet, gren.
- **Kırpma ve döndürme**, sürüklenebilir **önce / sonra** kaydırıcısı, yakınlaştırma, geri al / yinele.
- **9 pakette 60 filtre:** pakete veya türe göre gruplama, kendi filtrelerinizi kaydetme, tek tek filtreleri veya paketlerin tamamını (`.pack.json`) ve `.cube` LUT dosyalarını içe/dışa aktarma.
- Lightroom tarzı **kütüphane ve içe aktarma**, film şeridi, yıldız derecelendirme, **toplu işleme**, JPEG, PNG, WebP veya TIFF olarak dışa aktarma.
- Çoğu kameranın **RAW** dosyaları (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Yıkıcı olmayan: orijinal dosyalarınız asla değiştirilmez. Her şey bilgisayarınızda çalışır — bulut yok, hesap yok.

## İndirme (Python gerekmez)

Ubuntu / Debian için `.deb` veya `.AppImage` dosyasını [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) sayfasından alın:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Kaynak koddan çalıştırma

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Lisans

[MIT](LICENSE). Üçüncü taraf bileşenler ve model ağırlıkları: bkz. [NOTICE](NOTICE).

**Tam belgeler:** [English](README.md) · [Русский](README.ru.md)
