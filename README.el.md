# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · **Ελληνικά** · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

Το **Photo Editor AI** είναι δωρεάν επεξεργαστής φωτογραφιών ανοιχτού κώδικα: αυτόματη διόρθωση με τεχνητή νοημοσύνη, καμπύλη τόνων σαν του Photoshop, HSL, πακέτα φίλτρων με εισαγωγή και εξαγωγή, βιβλιοθήκη σαν του Lightroom και μαζική επεξεργασία. Η επεξεργασία είναι μη καταστροφική και όλα εκτελούνται τοπικά στον υπολογιστή σας.

## Στιγμιότυπα

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Δυνατότητες

- **Αυτόματη διόρθωση με ΤΝ:** έκθεση + χρώμα ή μόνο έκθεση, με προστασία των φωτεινών περιοχών από υπερέκθεση· το αποτέλεσμα μένει ως απλά ρυθμιστικά που μπορείτε να ρυθμίσετε.
- **Χειροκίνητη επεξεργασία:** έκθεση, αντίθεση, φώτα και σκιές, ισορροπία λευκού, καμπύλη τόνων σαν του Photoshop, HSL, οξύτητα, καθαρότητα, αφαίρεση ομίχλης, βινιέτα, κόκκος.
- **Περικοπή και περιστροφή**, ρυθμιστικό **πριν / μετά** που σύρεται, ζουμ, αναίρεση / επανάληψη.
- **60 φίλτρα σε 9 πακέτα:** ομαδοποίηση ανά πακέτο ή τύπο, αποθήκευση δικών σας, εισαγωγή και εξαγωγή μεμονωμένων φίλτρων ή ολόκληρων πακέτων (`.pack.json`) και LUT `.cube`.
- **Βιβλιοθήκη και εισαγωγή** σαν του Lightroom, ταινία μικρογραφιών, βαθμολογία με αστέρια, **μαζική επεξεργασία**, εξαγωγή σε JPEG, PNG, WebP ή TIFF.
- Αρχεία **RAW** των περισσότερων μηχανών (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Μη καταστροφική: τα πρωτότυπά σας δεν αλλάζουν ποτέ. Όλα τρέχουν στον υπολογιστή σας — χωρίς cloud και χωρίς λογαριασμό.

## Λήψη (χωρίς Python)

Κατεβάστε το `.deb` ή το `.AppImage` για Ubuntu / Debian από τη σελίδα [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Εκτέλεση από τον πηγαίο κώδικα

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Άδεια

[MIT](LICENSE). Εξαρτήματα τρίτων και βάρη μοντέλων: βλ. [NOTICE](NOTICE).

**Πλήρης τεκμηρίωση:** [English](README.md) · [Русский](README.ru.md)
