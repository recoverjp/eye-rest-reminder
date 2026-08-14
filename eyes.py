"""Detecção de "olhos fechados" usando MediaPipe Face Landmarker.

Usa a Tasks API do MediaPipe com *blendshapes* faciais. Dois deles indicam o
quanto cada olho está fechado:
  - eyeBlinkLeft  (0 = aberto, ~1 = fechado)
  - eyeBlinkRight (0 = aberto, ~1 = fechado)

Consideramos "olhos fechados" quando AMBOS passam de um limiar. Isso é usado
pelo loop principal para tratar olhos fechados por um tempo como descanso,
zerando o contador de tempo de tela.

Roda 100% local, na CPU. O modelo (~3 MB) é baixado automaticamente na 1ª vez.
"""

import os
import urllib.request

import config


MODEL_FILENAME = "face_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)

BLINK_LEFT = "eyeBlinkLeft"
BLINK_RIGHT = "eyeBlinkRight"


def _ensure_model() -> str:
    """Garante que o arquivo do modelo exista localmente; baixa se preciso."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)
    if not os.path.isfile(path):
        print(f"Baixando modelo facial ({MODEL_FILENAME}, ~3 MB)...")
        urllib.request.urlretrieve(MODEL_URL, path)
        print("  Modelo baixado.")
    return path


class EyeStateDetector:
    """Diz se os olhos estão fechados no frame."""

    def __init__(self, threshold: float = None):
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision
        except ImportError as exc:
            raise RuntimeError(
                'A detecção de "olhos fechados" requer o pacote "mediapipe". '
                "Instale com: pip install mediapipe — ou desative com "
                "ENABLE_EYES_CLOSED_REST = False em config.py."
            ) from exc

        self._mp = mp
        self.threshold = (
            config.EYE_CLOSED_THRESHOLD if threshold is None else threshold
        )
        model_path = _ensure_model()

        options = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=1,
            output_face_blendshapes=True,
        )
        self.landmarker = mp_vision.FaceLandmarker.create_from_options(options)

    def analyze(self, frame):
        """Roda o Face Landmarker uma vez e retorna um dict com métricas:

            {"present": bool,           # há rosto?
             "blink": float,            # média eyeBlink (0 aberto … ~1 fechado)
             "eyes_closed": bool,       # ambos os olhos fechados
             "face_width": float}       # largura do rosto / largura do quadro

        Retorna {"present": False, ...} se não houver rosto.
        """
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB, data=rgb
        )
        result = self.landmarker.detect(mp_image)
        if not result.face_blendshapes or not result.face_landmarks:
            return {"present": False, "blink": 0.0,
                    "eyes_closed": False, "face_width": 0.0}

        left = right = 0.0
        for cat in result.face_blendshapes[0]:
            if cat.category_name == BLINK_LEFT:
                left = cat.score
            elif cat.category_name == BLINK_RIGHT:
                right = cat.score
        blink = (left + right) / 2.0

        xs = [p.x for p in result.face_landmarks[0]]
        face_width = max(xs) - min(xs)  # já normalizado (0–1)

        return {
            "present": True,
            "blink": blink,
            "eyes_closed": left >= self.threshold and right >= self.threshold,
            "face_width": face_width,
        }

    def blink_scores(self, frame):
        """Retorna (left, right) dos blendshapes de piscar, ou None se sem rosto."""
        m = self.analyze(frame)
        return None if not m["present"] else (m["blink"], m["blink"])

    def eyes_closed(self, frame):
        """True se ambos os olhos fechados; False se abertos; None se sem rosto."""
        m = self.analyze(frame)
        return None if not m["present"] else m["eyes_closed"]
