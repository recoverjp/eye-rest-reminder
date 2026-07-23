"""Loop principal do eye-rest-reminder.

Monitora a webcam, conta o tempo contínuo em que uma pessoa/rosto é
detectado e dispara um alerta após o tempo limite configurado.

Execute com:  python main.py
Pare com Ctrl+C.
"""

import time
from datetime import datetime

import cv2

import config
from detector import create_detector
from notifier import send_alert


def _now() -> float:
    """Relógio monotônico (não sofre com ajustes de horário do sistema)."""
    return time.monotonic()


def _timestamp() -> str:
    """Hora atual formatada como [HH:MM:SS] para o log."""
    return datetime.now().strftime("[%H:%M:%S]")


def _format_duration(seconds: float) -> str:
    """Formata uma duração em segundos como HH:MM:SS."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> None:
    alert_after_seconds = config.ALERT_AFTER_MINUTES * 60
    cooldown_seconds = config.COOLDOWN_AFTER_ALERT_MINUTES * 60

    print("Iniciando eye-rest-reminder...")
    print(
        f"  Alerta após {config.ALERT_AFTER_MINUTES} min contínuos | "
        f"reset após {config.RESET_AFTER_SECONDS}s sem rosto | "
        f"cooldown de {config.COOLDOWN_AFTER_ALERT_MINUTES} min"
    )
    print(f"Carregando detector ({config.DETECTOR})...")

    detector = create_detector()

    cap = cv2.VideoCapture(config.WEBCAM_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        # Tenta sem o backend DSHOW (específico do Windows) como fallback.
        cap = cv2.VideoCapture(config.WEBCAM_INDEX)
    if not cap.isOpened():
        print(
            f"ERRO: não foi possível abrir a webcam (índice "
            f"{config.WEBCAM_INDEX}). Verifique se ela está conectada e se "
            f"nenhum outro programa a está usando."
        )
        return

    print("Webcam aberta. Monitorando... (Ctrl+C para sair)\n")

    # ----- Estado do contador -----
    session_start = None   # instante em que a presença contínua começou
    last_seen = None       # último instante em que houve detecção
    cooldown_until = 0.0   # não dispara novo alerta antes deste instante

    try:
        while True:
            loop_start = _now()

            ok, frame = cap.read()
            if not ok or frame is None:
                print(f"{_timestamp()} Falha ao capturar frame da webcam.")
                time.sleep(config.FRAME_INTERVAL_SECONDS)
                continue

            face_present = detector.detect(frame)
            now = _now()

            if face_present:
                if session_start is None:
                    session_start = now
                last_seen = now

                continuous = now - session_start
                print(
                    f"{_timestamp()} Rosto detectado — "
                    f"{_format_duration(continuous)} contínuos"
                )

                if continuous >= alert_after_seconds and now >= cooldown_until:
                    print(
                        f"{_timestamp()} >>> ALERTA! "
                        f"{config.ALERT_AFTER_MINUTES} min contínuos atingidos. "
                        f"Descanse os olhos!"
                    )
                    send_alert()
                    # Aguarda o cooldown antes de poder disparar de novo.
                    cooldown_until = now + cooldown_seconds
            else:
                if session_start is not None and last_seen is not None:
                    absence = now - last_seen
                    if absence > config.RESET_AFTER_SECONDS:
                        print(
                            f"{_timestamp()} Ausência de "
                            f"{_format_duration(absence)} — contador ZERADO."
                        )
                        session_start = None
                        last_seen = None
                        cooldown_until = 0.0
                    else:
                        print(
                            f"{_timestamp()} Sem rosto detectado — "
                            f"contador pausado (ausência: "
                            f"{_format_duration(absence)})"
                        )
                else:
                    print(
                        f"{_timestamp()} Sem rosto detectado — "
                        f"contador pausado"
                    )

            # Mantém ~1 frame por segundo, descontando o tempo já gasto.
            elapsed = _now() - loop_start
            sleep_time = config.FRAME_INTERVAL_SECONDS - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nEncerrando eye-rest-reminder. Até logo!")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
