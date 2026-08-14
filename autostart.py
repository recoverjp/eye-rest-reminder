"""Iniciar com o Windows — liga/desliga via registro do usuário (sem admin).

Cria/remove um valor em:
    HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run

Assim o app sobe sozinho quando o usuário faz login. É por usuário (HKCU), então
não precisa de privilégios de administrador.

Funciona tanto no .exe empacotado (aponta para o próprio .exe) quanto rodando
pelo código-fonte (aponta para o pythonw + tray.py).
"""

import os
import sys

try:
    import winreg  # só existe no Windows
except ImportError:  # noutro SO, tudo vira no-op
    winreg = None


APP_NAME = "eye-rest-reminder"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _launch_command() -> str:
    """Comando que o Windows executará no login (com aspas onde necessário)."""
    if getattr(sys, "frozen", False):
        # Empacotado: o próprio executável.
        return f'"{sys.executable}"'
    # Código-fonte: pythonw.exe (sem console) rodando o tray.py.
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    launcher = pyw if os.path.isfile(pyw) else sys.executable
    tray = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tray.py")
    return f'"{launcher}" "{tray}"'


def is_supported() -> bool:
    """True se dá para mexer no autostart (Windows com winreg)."""
    return winreg is not None


def is_enabled() -> bool:
    """True se o app já está configurado para iniciar com o Windows."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            value, _type = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable() -> bool:
    """Passa a iniciar com o Windows. Retorna True em caso de sucesso."""
    if winreg is None:
        return False
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())
        return True
    except OSError:
        return False


def disable() -> bool:
    """Deixa de iniciar com o Windows. Retorna True em caso de sucesso."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        return True
    except FileNotFoundError:
        return True  # já não estava lá
    except OSError:
        return False


def toggle() -> bool:
    """Inverte o estado. Retorna o novo estado (True = ligado)."""
    if is_enabled():
        disable()
        return False
    enable()
    return is_enabled()
