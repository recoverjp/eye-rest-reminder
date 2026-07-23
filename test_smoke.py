"""Teste rápido (smoke test) do eye-rest-reminder.

Verifica, sem esperar 1 hora, que:
  1. A webcam abre e captura um frame.
  2. O modelo YOLO carrega e roda a detecção nesse frame.

Execute com:  python test_smoke.py
"""

import sys

import cv2

import config
from detector import create_detector


def main() -> int:
    print("[1/3] Abrindo webcam (índice "
          f"{config.WEBCAM_INDEX})...")
    cap = cv2.VideoCapture(config.WEBCAM_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(config.WEBCAM_INDEX)
    if not cap.isOpened():
        print("  FALHOU: não foi possível abrir a webcam.")
        return 1

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        print("  FALHOU: webcam abriu mas não retornou frame.")
        return 1
    print(f"  OK: frame capturado com resolução {frame.shape[1]}x{frame.shape[0]}.")

    print(f"[2/3] Carregando detector ({config.DETECTOR})...")
    detector = create_detector()
    print("  OK: detector carregado.")

    print("[3/3] Rodando detecção no frame...")
    present = detector.detect(frame)
    print(f"  OK: detecção executada. Presença detectada? {'SIM' if present else 'NÃO'}")

    print("\nSmoke test concluído com sucesso. O main.py está pronto para rodar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
