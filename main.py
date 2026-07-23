"""Loop principal do eye-rest-reminder.

Monitora a webcam, conta o tempo contínuo em que uma pessoa/rosto é
detectado e dispara um alerta após o tempo limite configurado.

Execute com:  python main.py
Pare com Ctrl+C.
"""

import sys
import time
from datetime import datetime

import cv2

import config

# Garante que emojis (✋👀) não quebrem o print no console do Windows (cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from detector import create_detector
from notifier import send_alert, send_hand_on_head_alert


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


def _confirm_hand_on_head(cap, hand_detector) -> bool:
    """Re-checa se a mão CONTINUA na cabeça durante a janela de confirmação.

    Amostra a webcam a cada 1s por `HAND_ON_HEAD_CONFIRM_SECONDS`. Retorna
    True só se a mão estiver presente em TODAS as amostras (gesto sustentado).
    Assim que a mão sumir uma vez, retorna False (foi passageiro — coçada
    rápida, ajeitar óculos, etc.).
    """
    seconds = config.HAND_ON_HEAD_CONFIRM_SECONDS
    if seconds <= 0:
        return True

    print(
        f"{_timestamp()} Mão na cabeça detectada — confirmando por "
        f"{seconds}s (a mão continua lá?)..."
    )
    deadline = _now() + seconds
    samples = 0
    while _now() < deadline:
        time.sleep(1.0)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        samples += 1
        if not hand_detector.detect(frame):
            return False  # a mão saiu → gesto passageiro
    return samples > 0


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

    # Detector opcional de "mão na cabeça". Se o mediapipe não estiver
    # instalado (ou falhar), apenas desativa o recurso — não derruba a app.
    hand_detector = None
    if config.ENABLE_HAND_ON_HEAD:
        try:
            from gesture import HandOnHeadDetector
            print("Carregando detector de 'mão na cabeça' (mediapipe)...")
            hand_detector = HandOnHeadDetector()
            print(
                f"  Ativo. Cooldown de "
                f"{config.HAND_ON_HEAD_COOLDOWN_SECONDS}s entre alertas."
            )
        except Exception as exc:
            print(f"  AVISO: 'mão na cabeça' desativado — {exc}")
            hand_detector = None

    # Detector opcional de "olhos fechados" (para tratar como descanso).
    eye_detector = None
    if config.ENABLE_EYES_CLOSED_REST:
        try:
            from eyes import EyeStateDetector
            print("Carregando detector de 'olhos fechados' (mediapipe)...")
            eye_detector = EyeStateDetector()
            print(
                f"  Ativo. Olhos fechados por "
                f"{config.EYES_CLOSED_REST_SECONDS}s contam como descanso."
            )
        except Exception as exc:
            print(f"  AVISO: 'olhos fechados' desativado — {exc}")
            eye_detector = None

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

    # Aquece a câmera: os primeiros frames costumam vir escuros (auto-exposição
    # ainda ajustando), o que atrapalha a detecção. Descartamos alguns.
    for _ in range(5):
        cap.read()
        time.sleep(0.2)

    print("Webcam aberta. Monitorando... (Ctrl+C para sair)\n")

    # ----- Estado do contador -----
    session_start = None   # instante em que a presença contínua começou
    last_seen = None       # último instante em que houve detecção
    cooldown_until = 0.0   # não dispara novo alerta antes deste instante
    hand_cooldown_until = 0.0  # cooldown do alerta de "mão na cabeça"
    eyes_closed_since = None    # instante em que os olhos começaram fechados

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

            # ----- Detecção opcional de "mão na cabeça" -----
            if hand_detector is not None:
                try:
                    if hand_detector.detect(frame):
                        if now < hand_cooldown_until:
                            print(
                                f"{_timestamp()} Mão na cabeça (em cooldown)"
                            )
                        elif _confirm_hand_on_head(cap, hand_detector):
                            print(
                                f"{_timestamp()} >>> MÃO NA CABEÇA confirmada! "
                                f"Notificando."
                            )
                            send_hand_on_head_alert()
                            hand_cooldown_until = (
                                _now() + config.HAND_ON_HEAD_COOLDOWN_SECONDS
                            )
                        else:
                            print(
                                f"{_timestamp()} Mão na cabeça passageira "
                                f"(coçada rápida) — ignorado."
                            )
                except Exception as exc:
                    print(f"{_timestamp()} Erro na detecção de gesto: {exc}")

            # Estado dos olhos (fechado/aberto), se o detector estiver ativo.
            eyes_closed = None
            if face_present and eye_detector is not None:
                try:
                    eyes_closed = eye_detector.eyes_closed(frame)
                except Exception as exc:
                    print(f"{_timestamp()} Erro na detecção de olhos: {exc}")

            if face_present and eyes_closed:
                # Olhos fechados: possível descanso — não conta tempo de tela.
                last_seen = now
                if eyes_closed_since is None:
                    eyes_closed_since = now
                closed_dur = now - eyes_closed_since

                if (session_start is not None
                        and closed_dur >= config.EYES_CLOSED_REST_SECONDS):
                    print(
                        f"{_timestamp()} Olhos fechados por "
                        f"{_format_duration(closed_dur)} — DESCANSO! "
                        f"Contador de tela zerado."
                    )
                    session_start = None
                    cooldown_until = 0.0
                    eyes_closed_since = None
                else:
                    restante = max(
                        0,
                        int(config.EYES_CLOSED_REST_SECONDS - closed_dur),
                    )
                    print(
                        f"{_timestamp()} Olhos fechados "
                        f"({_format_duration(closed_dur)}) — descanso em "
                        f"~{restante}s"
                    )

            elif face_present:
                # Rosto presente e olhos abertos (ou detector desligado).
                eyes_closed_since = None
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
                eyes_closed_since = None
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
