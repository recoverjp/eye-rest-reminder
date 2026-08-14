"""Ícone na bandeja do sistema (systray) com menu para ligar/desligar recursos.

Executa o monitoramento (`main.run`) numa thread em segundo plano e mostra um
ícone perto do relógio do Windows. No menu (clique com o botão direito) você
liga/desliga cada recurso em tempo real e encerra o app pelo item "Sair".

Rode com:  pythonw tray.py   (sem janela)  ou  python tray.py  (com log)
"""

import threading

# Antes de qualquer print/import pesado: no .exe sem console, redireciona a
# saída para um arquivo de log (senão o primeiro print derruba o programa).
from paths import setup_frozen_io

setup_frozen_io()

import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

import autostart
import main
from notifier import notify
from settings import Settings, FEATURES
from stats import DailyStats


def _ask_autostart_on_first_run(settings: Settings) -> None:
    """Na 1ª execução, pergunta (caixa de diálogo) se quer iniciar com o Windows.

    Só pergunta uma vez — guarda a resposta em settings ("asked_autostart").
    Silencioso e sem efeito se o autostart não for suportado ou algo falhar.
    """
    if settings.get_value("asked_autostart", False) or not autostart.is_supported():
        return
    try:
        import ctypes

        # MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2 | MB_SETFOREGROUND | MB_TOPMOST
        # MB_DEFBUTTON2 deixa o "Não" como padrão: um Enter acidental NÃO ativa
        # o autostart — só um clique deliberado em "Sim".
        flags = 0x04 | 0x20 | 0x100 | 0x10000 | 0x40000
        answer = ctypes.windll.user32.MessageBoxW(
            0,
            "Quer que o eye-rest-reminder inicie automaticamente junto com o "
            "Windows?\n\nVocê pode mudar isso quando quiser pelo menu do ícone "
            "na bandeja (botão direito).",
            "eye-rest-reminder",
            flags,
        )
        if answer == 6:  # IDYES
            if autostart.enable():
                notify("Início automático ativado 🚀",
                       "O eye-rest-reminder vai abrir junto com o Windows.")
    except Exception:
        pass
    finally:
        # Marca como perguntado mesmo se algo falhar, para não insistir.
        settings.set_value("asked_autostart", True)


def _make_icon_image() -> Image.Image:
    """Desenha um pequeno olho para o ícone da bandeja."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 20, 60, 44), fill=(245, 245, 245, 255),
              outline=(40, 40, 40, 255), width=2)      # contorno do olho
    d.ellipse((25, 20, 44, 44), fill=(60, 120, 220, 255))  # íris
    d.ellipse((30, 26, 39, 38), fill=(20, 20, 20, 255))    # pupila
    d.ellipse((32, 27, 36, 31), fill=(255, 255, 255, 255)) # brilho
    return img


def run_tray() -> None:
    settings = Settings()
    stats = DailyStats()
    stop_event = threading.Event()
    calibrate_posture = threading.Event()

    # Monitoramento roda numa thread; o ícone fica na thread principal (exigência
    # do pystray no Windows).
    worker = threading.Thread(
        target=main.run,
        args=(settings, stop_event, stats, calibrate_posture),
        daemon=True,
    )
    worker.start()

    def make_toggle(key: str, label: str) -> MenuItem:
        return MenuItem(
            label,
            lambda icon, item: settings.toggle(key),
            checked=lambda item: settings.get(key),
        )

    def on_summary(icon, item):
        notify("Resumo do dia 📊", stats.summary())

    def on_calibrate(icon, item):
        calibrate_posture.set()
        notify("Calibrar postura 🧍",
               "Sente reto e olhe para a tela — vou salvar sua postura de "
               "referência nos próximos segundos.")

    def on_autostart(icon, item):
        ligado = autostart.toggle()
        if ligado:
            notify("Início automático ativado 🚀",
                   "O eye-rest-reminder vai abrir junto com o Windows.")
        else:
            notify("Início automático desativado",
                   "O eye-rest-reminder não vai mais abrir junto com o Windows.")

    def on_quit(icon, item):
        stop_event.set()
        icon.stop()

    autostart_item = MenuItem(
        "Iniciar com o Windows",
        on_autostart,
        checked=lambda item: autostart.is_enabled(),
        visible=autostart.is_supported(),
    )

    menu = Menu(
        MenuItem("eye-rest-reminder", None, enabled=False),
        Menu.SEPARATOR,
        *[make_toggle(key, label) for key, label, _default in FEATURES],
        Menu.SEPARATOR,
        MenuItem("Calibrar postura (sente reto)", on_calibrate),
        MenuItem("Resumo do dia", on_summary),
        autostart_item,
        Menu.SEPARATOR,
        MenuItem("Sair", on_quit),
    )

    # Na primeira vez que o app roda, pergunta se quer iniciar com o Windows.
    _ask_autostart_on_first_run(settings)

    icon = pystray.Icon(
        "eye-rest-reminder", _make_icon_image(),
        "eye-rest-reminder", menu
    )
    icon.run()  # bloqueia até "Sair"

    stop_event.set()
    worker.join(timeout=5)


if __name__ == "__main__":
    run_tray()
