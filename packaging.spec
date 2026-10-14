# PyInstaller: pyinstaller --noconfirm packaging.spec
from PyInstaller.utils.hooks import collect_all

raw_datas, raw_binaries, raw_hidden = collect_all("rawpy")

a = Analysis(
    ["run_app.py"],
    pathex=["."],
    datas=[("assets", "assets"), ("app/services/presets_site.json", "app/services")] + raw_datas,
    binaries=raw_binaries,
    hiddenimports=raw_hidden,
    excludes=["tkinter", "PySide6.QtWebEngineCore", "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtPdf", "PySide6.QtOpenGL",
              "torch", "matplotlib", "scipy", "pandas", "onnx", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="Photo-Editor-AI", console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="Photo-Editor-AI")
