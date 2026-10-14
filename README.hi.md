# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · **हिन्दी** · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** एक मुफ़्त, ओपन-सोर्स फ़ोटो एडिटर है: AI से स्वचालित सुधार, Photoshop जैसा टोन कर्व, HSL, आयात-निर्यात योग्य फ़िल्टर पैक, Lightroom जैसी लाइब्रेरी और बैच प्रोसेसिंग। संपादन गैर-विनाशकारी है और सब कुछ आपके कंप्यूटर पर ही चलता है।

## स्क्रीनशॉट

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## सुविधाएँ

- **AI स्वचालित सुधार:** एक्सपोज़र + रंग या केवल एक्सपोज़र, हाइलाइट जलने से सुरक्षा के साथ; परिणाम सामान्य स्लाइडर के रूप में रहता है जिन्हें आप बारीकी से बदल सकते हैं।
- **मैन्युअल संपादन:** एक्सपोज़र, कंट्रास्ट, हाइलाइट और शैडो, व्हाइट बैलेंस, Photoshop जैसा टोन कर्व, HSL, शार्पनेस, क्लैरिटी, धुंध हटाना, विनेट, ग्रेन।
- **क्रॉप और रोटेट**, खींचने योग्य **पहले / बाद** स्लाइडर, ज़ूम, पूर्ववत / फिर से करें।
- **9 पैक में 60 फ़िल्टर:** पैक या प्रकार के अनुसार समूह, अपने फ़िल्टर सहेजें, एकल फ़िल्टर या पूरे पैक (`.pack.json`) और `.cube` LUT आयात-निर्यात करें।
- Lightroom जैसी **लाइब्रेरी और आयात**, फ़िल्मस्ट्रिप, स्टार रेटिंग, **बैच प्रोसेसिंग**, JPEG, PNG, WebP या TIFF में निर्यात।
- अधिकांश कैमरों की **RAW** फ़ाइलें (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …)।
- गैर-विनाशकारी: आपकी मूल फ़ाइलें कभी नहीं बदलतीं। सब कुछ आपके कंप्यूटर पर चलता है — न क्लाउड, न खाता।

## डाउनलोड (Python की ज़रूरत नहीं)

Ubuntu / Debian के लिए `.deb` या `.AppImage` [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) पेज से लें:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## सोर्स कोड से चलाएँ

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## लाइसेंस

[MIT](LICENSE)। तृतीय-पक्ष घटक और मॉडल वज़न: देखें [NOTICE](NOTICE)।

**पूर्ण दस्तावेज़:** [English](README.md) · [Русский](README.ru.md)
