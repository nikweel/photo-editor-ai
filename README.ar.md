# Photo Editor AI

**العربية** · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** برنامج مجاني ومفتوح المصدر لتحرير الصور على سطح المكتب، يضم تصحيحًا تلقائيًا بالذكاء الاصطناعي، ومنحنى النغمات بأسلوب Photoshop، وHSL، وحزم فلاتر قابلة للاستيراد والتصدير، ومكتبة بأسلوب Lightroom ومعالجة دفعية. التعديل غير مدمّر ويعمل كل شيء محليًا على جهازك.

## لقطات الشاشة

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## المزايا

- **تصحيح تلقائي بالذكاء الاصطناعي:** التعريض + اللون أو التعريض فقط، مع حماية الإضاءات العالية من الاحتراق؛ تبقى النتيجة منزلقات عادية يمكنك ضبطها.
- **تحرير يدوي:** التعريض، التباين، الإضاءات العالية والظلال، توازن اللون الأبيض، منحنى نغمات بأسلوب Photoshop، HSL، الحدة، الوضوح، إزالة الضباب، التظليل الجانبي، الحبيبات.
- **قص وتدوير**، منزلق **قبل / بعد** قابل للسحب، تكبير، تراجع / إعادة.
- **60 فلترًا في 9 حزم:** تجميع حسب الحزمة أو النوع، حفظ فلاترك، واستيراد وتصدير فلاتر منفردة أو حزم كاملة (`.pack.json`) وملفات `.cube`.
- **مكتبة واستيراد** بأسلوب Lightroom، شريط الصور، تقييم بالنجوم، **معالجة دفعية**، تصدير إلى JPEG وPNG وWebP وTIFF.
- ملفات **RAW** لمعظم الكاميرات (CR2 وCR3 وNEF وARW وDNG وORF وRAF وRW2 …).
- غير مدمّر: لا تتغير ملفاتك الأصلية أبدًا. كل شيء يعمل على جهازك — بلا سحابة وبلا حساب.

## التنزيل (بدون Python)

نزّل ملف `.deb` أو `.AppImage` لنظام Ubuntu / Debian من صفحة [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## التشغيل من الشيفرة المصدرية

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## الترخيص

[MIT](LICENSE). المكوّنات الخارجية وأوزان النماذج: راجع [NOTICE](NOTICE).

**التوثيق الكامل:** [English](README.md) · [Русский](README.ru.md)
