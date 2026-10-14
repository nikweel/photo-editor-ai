# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · **Suomi** · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI** on ilmainen avoimen lähdekoodin valokuvaeditori: tekoälyn automaattinen korjaus, Photoshopin kaltainen sävykäyrä, HSL, tuotavat ja vietävät suodatinpaketit, Lightroomin kaltainen kirjasto ja eräajo. Muokkaus on tuhoamatonta ja kaikki toimii paikallisesti tietokoneellasi.

## Kuvakaappaukset

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Ominaisuudet

- **Tekoälyn automaattinen korjaus:** valotus + väri tai vain valotus, ylivalottumisen suojauksella; tulos jää tavallisiksi säätimiksi, joita voit hienosäätää.
- **Käsinmuokkaus:** valotus, kontrasti, kirkkaat ja varjot, valkotasapaino, Photoshopin kaltainen sävykäyrä, HSL, terävyys, selkeys, sumunpoisto, vinjetointi, rae.
- **Rajaus ja kierto**, vedettävä **ennen / jälkeen** -liukusäädin, zoomaus, kumoa / tee uudelleen.
- **60 suodatinta 9 paketissa:** ryhmittely paketeittain tai tyypeittäin, omien tallennus, yksittäisten suodattimien tai kokonaisten pakettien (`.pack.json`) sekä `.cube`-LUT:ien tuonti ja vienti.
- **Kirjasto ja tuonti** Lightroomin tapaan, filmiliuska, tähtiarvostelut, **eräajo**, vienti JPEG-, PNG-, WebP- tai TIFF-muotoon.
- Useimpien kameroiden **RAW**-tiedostot (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Tuhoamaton: alkuperäisiä ei koskaan muuteta. Kaikki toimii omalla koneellasi — ei pilveä eikä tiliä.

## Lataus (ilman Pythonia)

Lataa `.deb` tai `.AppImage` Ubuntulle / Debianille [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest)-sivulta:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Ajo lähdekoodista

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Lisenssi

[MIT](LICENSE). Kolmannen osapuolen komponentit ja mallien painot: katso [NOTICE](NOTICE).

**Täydellinen dokumentaatio:** [English](README.md) · [Русский](README.ru.md)
