"""Notificação nativa do Windows + som de alerta."""

import os

import config


def _play_sound() -> None:
    """Toca um som de alerta.

    Usa o arquivo .wav configurado em `config.ALERT_WAV_FILE` se existir;
    caso contrário, emite uma sequência de beeps com o `winsound`.
    """
    try:
        import winsound
    except ImportError:
        # winsound só existe no Windows; em outros SOs apenas ignora o som.
        return

    wav = config.ALERT_WAV_FILE
    if wav and os.path.isfile(wav):
        try:
            winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass  # se falhar, cai no beep padrão abaixo

    # Beep simples: três tons curtos.
    try:
        for _ in range(3):
            winsound.Beep(880, 250)  # frequência 880 Hz, 250 ms
    except Exception:
        # Fallback final: beep padrão do sistema.
        winsound.MessageBeep()


def _show_notification(title: str, message: str) -> None:
    """Exibe uma notificação popup nativa do Windows.

    Tenta usar `plyer` primeiro (mais portável) e, se indisponível, recorre
    ao `win10toast`.
    """
    duration = config.NOTIFICATION_DURATION_SECONDS

    # 1) Tenta via plyer
    try:
        from plyer import notification

        notification.notify(
            title=title,
            message=message,
            app_name="eye-rest-reminder",
            timeout=duration,
        )
        return
    except Exception:
        pass

    # 2) Fallback via win10toast
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        # threaded=True para não bloquear o loop principal.
        toaster.show_toast(title, message, duration=duration, threaded=True)
        return
    except Exception:
        pass

    # 3) Fallback final: apenas imprime no terminal.
    print(f"\n{'=' * 60}\n{title}\n{message}\n{'=' * 60}\n")


def notify(title: str, message: str) -> None:
    """Dispara uma notificação (popup + som) com título/mensagem dados."""
    _show_notification(title, message)
    _play_sound()


def send_alert() -> None:
    """Alerta de descanso dos olhos (usa título/mensagem do config)."""
    notify(config.ALERT_TITLE, config.ALERT_MESSAGE)


def send_hand_on_head_alert() -> None:
    """Alerta de 'mão na cabeça' (usa título/mensagem do config)."""
    notify(config.HAND_ON_HEAD_TITLE, config.HAND_ON_HEAD_MESSAGE)
