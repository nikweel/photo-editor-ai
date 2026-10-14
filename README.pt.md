# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · **Português** · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

O **Photo Editor AI** é um editor de fotos gratuito e de código aberto: correção automática com IA, curva de tons ao estilo do Photoshop, HSL, pacotes de filtros importáveis e exportáveis, biblioteca ao estilo do Lightroom e processamento em lote. A edição é não destrutiva e tudo roda localmente no seu computador.

## Capturas de tela

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## Recursos

- **Correção automática com IA:** exposição + cor ou só exposição, com proteção contra realces estourados; o resultado continua como controles deslizantes comuns que você pode ajustar.
- **Edição manual:** exposição, contraste, realces e sombras, balanço de brancos, curva de tons ao estilo do Photoshop, HSL, nitidez, clareza, remoção de névoa, vinheta, granulação.
- **Recorte e rotação**, controle **antes / depois** arrastável, zoom, desfazer / refazer.
- **60 filtros em 9 pacotes:** agrupamento por pacote ou tipo, salve os seus, importe e exporte filtros avulsos ou pacotes inteiros (`.pack.json`) e LUTs `.cube`.
- **Biblioteca e importação** ao estilo do Lightroom, tira de miniaturas, avaliação por estrelas, **processamento em lote**, exportação para JPEG, PNG, WebP ou TIFF.
- Arquivos **RAW** da maioria das câmeras (CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 …).
- Não destrutivo: seus originais nunca são alterados. Tudo roda no seu computador — sem nuvem e sem conta.

## Download (sem Python)

Baixe o `.deb` ou o `.AppImage` para Ubuntu / Debian na página [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest):

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## Executar a partir do código-fonte

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## Licença

[MIT](LICENSE). Componentes de terceiros e pesos dos modelos: veja [NOTICE](NOTICE).

**Documentação completa:** [English](README.md) · [Русский](README.ru.md)
