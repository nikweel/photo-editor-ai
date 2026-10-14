# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · **Polski** · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** to darmowy edytor zdjęć o otwartym kodzie: automatyczna korekcja za pomocą AI, krzywa tonalna jak w Photoshopie, HSL, pakiety filtrów z importem i eksportem, biblioteka jak w Lightroomie oraz przetwarzanie wsadowe. Edycja jest nieniszcząca, a wszystko działa lokalnie na Twoim komputerze.

## Zrzuty ekranu

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Funkcje

- **Automatyczna korekcja AI:** ekspozycja + kolor lub sama ekspozycja, z ochroną świateł przed przepaleniem; wynik pozostaje zwykłymi suwakami, które możesz dopracować.
- **Edycja ręczna:** ekspozycja, kontrast, światła i cienie, balans bieli, krzywa tonalna jak w Photoshopie, HSL, ostrość, przejrzystość, usuwanie mgły, winietowanie, ziarno.
- **Kadrowanie i obrót**, przeciągany suwak **przed / po**, powiększanie, cofnij / ponów.
- **60 filtrów w 9 pakietach:** grupowanie według pakietów lub typów, zapisywanie własnych, import i eksport pojedynczych filtrów lub całych pakietów (`.pack.json`) oraz LUT-ów `.cube`.
- **Biblioteka i import** jak w Lightroomie, pasek miniatur, oceny gwiazdkami, **przetwarzanie wsadowe**, eksport do JPEG, PNG, WebP lub TIFF.
- Pliki **RAW** większości aparatów (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Nieniszcząco: oryginały nigdy nie są zmieniane. Wszystko działa na Twoim komputerze — bez chmury i bez konta.

## Pobieranie (bez Pythona)

Pobierz `.deb` lub `.AppImage` dla Ubuntu / Debiana ze strony [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Uruchomienie ze źródeł

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licencja

[MIT](LICENSE). Komponenty stron trzecich i wagi modeli: zobacz [NOTICE](NOTICE).

**Pełna dokumentacja:** [English](README.md) · [Русский](README.ru.md)
