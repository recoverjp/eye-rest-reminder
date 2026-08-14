# -*- mode: python ; coding: utf-8 -*-
"""Especificação do PyInstaller para gerar o eye-rest-reminder.exe (arquivo único).

O ponto de entrada é o tray.py (ícone na bandeja). O MediaPipe precisa que a
gente colete explicitamente seus arquivos de dados (modelos .tflite/.binarypb) e
bibliotecas nativas (_framework_bindings.pyd) — é o que o collect_all faz abaixo.

Build:  pyinstaller eye-rest-reminder.spec --noconfirm
Saída:  dist/eye-rest-reminder.exe
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files

datas = []
binaries = []
hiddenimports = []

# MediaPipe: precisa de TODOS os seus dados + binários nativos + submódulos.
_d, _b, _h = collect_all("mediapipe")
datas += _d
binaries += _b
hiddenimports += _h

# OpenCV: os XMLs do Haar Cascade (cv2/data/*.xml) NÃO são coletados sozinhos.
# Sem eles o detector de rosto padrão ("haar") não carrega.
datas += collect_data_files("cv2")

# Notificações WinRT (windows-toasts usa o pacote winsdk/winrt em runtime).
for _pkg in ("winsdk", "windows_toasts"):
    try:
        _d, _b, _h = collect_all(_pkg)
        datas += _d
        binaries += _b
        hiddenimports += _h
    except Exception:
        pass

# Backends carregados dinamicamente que o PyInstaller não enxerga sozinho.
hiddenimports += [
    "pystray._win32",                       # backend de bandeja no Windows
    "plyer.platforms.win.notification",     # fallback de notificação
    "win32timezone",                        # usado pelo pywin32 (win10toast)
]

a = Analysis(
    ["tray.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # YOLO/torch são opcionais e enormes — nunca entram no .exe.
    excludes=["torch", "torchvision", "ultralytics", "tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="eye-rest-reminder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # sem janela de terminal (roda na bandeja)
    disable_windowed_traceback=False,
    icon="assets/icon.ico",
)
