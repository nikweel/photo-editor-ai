# Photo Editor AI

[العربية](README.ar.md) · [Български](README.bg.md) · [中文（简体）](README.zh.md) · [繁體中文](README.zh-TW.md) · [Hrvatski](README.hr.md) · [Čeština](README.cs.md) · [Dansk](README.da.md) · [Nederlands](README.nl.md) · [English](README.md) · [Suomi](README.fi.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Ελληνικά](README.el.md) · [हिन्दी](README.hi.md) · [Magyar](README.hu.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [日本語](README.ja.md) · **한국어** · [Lietuvių](README.lt.md) · [Norsk](README.nb.md) · [Polski](README.pl.md) · [Português](README.pt.md) · [Română](README.ro.md) · [Русский](README.ru.md) · [Slovenčina](README.sk.md) · [Español](README.es.md) · [Svenska](README.sv.md) · [Türkçe](README.tr.md) · [Українська](README.uk.md)

**Photo Editor AI**는 무료 오픈소스 사진 편집기입니다. AI 자동 보정, Photoshop 스타일 톤 커브, HSL, 가져오기·내보내기가 가능한 필터 팩, Lightroom 스타일 라이브러리, 일괄 처리를 제공합니다. 편집은 비파괴 방식이며 모든 작업은 내 컴퓨터에서 실행됩니다.

## 스크린샷

![Main window](docs/screenshots/main.png)
![Before / After](docs/screenshots/compare.png)
![Filter packs](docs/screenshots/filters.png)
![Manual adjustments](docs/screenshots/manual.png)

## 기능

- **AI 자동 보정:** 노출 + 색상 또는 노출만, 하이라이트 날림을 방지하며 결과는 일반 슬라이더로 남아 직접 미세 조정할 수 있습니다.
- **수동 편집:** 노출, 대비, 하이라이트와 그림자, 화이트 밸런스, Photoshop 스타일 톤 커브, HSL, 선명도, 명료도, 안개 제거, 비네트, 그레인.
- **자르기와 회전**, 드래그할 수 있는 **전 / 후** 슬라이더, 확대/축소, 실행 취소 / 다시 실행.
- **9개 팩의 필터 60종:** 팩 또는 유형별 그룹화, 내 필터 저장, 개별 필터 또는 팩 전체(`.pack.json`)와 `.cube` LUT 가져오기·내보내기.
- Lightroom 스타일 **라이브러리와 가져오기**, 필름스트립, 별점, **일괄 처리**, JPEG·PNG·WebP·TIFF로 내보내기.
- 대부분 카메라의 **RAW** 파일(CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2 등).
- 비파괴: 원본은 절대 변경되지 않습니다. 모든 것이 내 컴퓨터에서 실행되며 클라우드도 계정도 필요 없습니다.

## 다운로드 (Python 불필요)

Ubuntu / Debian용 `.deb` 또는 `.AppImage`를 [Releases](https://github.com/nikweel/photo-editor-ai/releases/latest) 페이지에서 받으세요:

- **Ubuntu / Debian:** `.deb` (`sudo apt install ./Photo-Editor-AI-<version>-amd64.deb`) or `.AppImage`
- **Windows:** `Photo-Editor-AI-<version>-Setup.exe`
- **macOS:** `Photo-Editor-AI-<version>-macos-arm64.dmg` (Apple silicon) / `-macos-intel.dmg`

## 소스에서 실행

```bash
git clone https://github.com/nikweel/photo-editor-ai.git
cd photo-editor-ai
uv sync
uv run python -m app.main
```

## 라이선스

[MIT](LICENSE). 서드파티 구성 요소와 모델 가중치: [NOTICE](NOTICE) 참조.

**전체 문서:** [English](README.md) · [Русский](README.ru.md)
