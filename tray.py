"""Ícone na bandeja do sistema (systray) com menu para ligar/desligar recursos.

Executa o monitoramento (`main.run`) numa thread em segundo plano e mostra um
ícone perto do relógio do Windows. No menu (clique com o botão direito) você
liga/desliga cada recurso em tempo real e encerra o app pelo item "Sair".

Rode com:  pythonw tray.py   (sem janela)  ou  python tray.py  (com log)
"""

import threading

import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

import main
from notifier import notify
from settings import Settings, FEATURES
from stats import DailyStats


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

    def on_quit(icon, item):
        stop_event.set()
        icon.stop()

    menu = Menu(
        MenuItem("eye-rest-reminder", None, enabled=False),
        Menu.SEPARATOR,
        *[make_toggle(key, label) for key, label, _default in FEATURES],
        Menu.SEPARATOR,
        MenuItem("Calibrar postura (sente reto)", on_calibrate),
        MenuItem("Resumo do dia", on_summary),
        Menu.SEPARATOR,
        MenuItem("Sair", on_quit),
    )

    icon = pystray.Icon(
        "eye-rest-reminder", _make_icon_image(),
        "eye-rest-reminder", menu
    )
    icon.run()  # bloqueia até "Sair"

    stop_event.set()
    worker.join(timeout=5)


if __name__ == "__main__":
    run_tray()
