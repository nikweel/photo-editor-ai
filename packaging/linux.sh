#!/bin/sh
# Использование: packaging/linux.sh <версия>  (после pyinstaller; dist/Photo-Editor-AI) -> release/*.deb и release/*.AppImage
set -e
VER="${1:-0.0.0}"; SRC=dist/Photo-Editor-AI; OUT=release; mkdir -p "$OUT"
DESKTOP='[Desktop Entry]
Type=Application
Name=Photo Editor AI
Comment=Photo editor with AI auto-correction, filters and batch processing
Comment[ru]=Фоторедактор с ИИ-автокоррекцией, фильтрами и пакетной обработкой
Exec=Photo-Editor-AI
Icon=photo-editor-ai
Categories=Graphics;Photography;
Terminal=false
StartupWMClass=photo-editor-ai'

# --- .deb ---
P=build/deb; rm -rf "$P"; mkdir -p "$P/DEBIAN" "$P/opt" "$P/usr/bin" "$P/usr/share/applications" "$P/usr/share/icons/hicolor/512x512/apps"
cp -r "$SRC" "$P/opt/photo-editor-ai"
ln -s /opt/photo-editor-ai/Photo-Editor-AI "$P/usr/bin/photo-editor-ai"
printf '%s\n' "$DESKTOP" | sed 's|^Exec=.*|Exec=/opt/photo-editor-ai/Photo-Editor-AI|' > "$P/usr/share/applications/photo-editor-ai.desktop"
cp assets/icon.png "$P/usr/share/icons/hicolor/512x512/apps/photo-editor-ai.png"
cat > "$P/DEBIAN/control" <<EOT
Package: photo-editor-ai
Version: $VER
Section: graphics
Priority: optional
Architecture: amd64
Maintainer: Nikolay Fedotov <nikweel@gmail.com>
Depends: libgl1, libxkbcommon-x11-0, libxcb-cursor0
Homepage: https://github.com/nikweel/photo-editor-ai
Description: Photo editor with AI auto-correction, filters and batch processing
 Non-destructive editing, tone curve, HSL, filter packs, Lightroom-style library.
 Everything runs locally.
EOT
dpkg-deb --build --root-owner-group "$P" "$OUT/Photo-Editor-AI-$VER-amd64.deb"

# --- AppImage ---
A=build/AppDir; rm -rf "$A"; mkdir -p "$A/usr/lib"
cp -r "$SRC" "$A/usr/lib/photo-editor-ai"
printf '%s\n' "$DESKTOP" > "$A/photo-editor-ai.desktop"
cp assets/icon.png "$A/photo-editor-ai.png"; cp assets/icon.png "$A/.DirIcon"
printf '#!/bin/sh\nHERE="$(dirname "$(readlink -f "$0")")"\nexec "$HERE/usr/lib/photo-editor-ai/Photo-Editor-AI" "$@"\n' > "$A/AppRun"; chmod +x "$A/AppRun"
[ -x build/appimagetool ] || { mkdir -p build; curl -fsSL -o build/appimagetool https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage; chmod +x build/appimagetool; }
ARCH=x86_64 build/appimagetool --appimage-extract-and-run "$A" "$OUT/Photo-Editor-AI-$VER-x86_64.AppImage"
ls -la "$OUT"
