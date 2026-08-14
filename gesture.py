"""Detecção de gesto "mão na cabeça" usando MediaPipe (Pose Landmarker).

Usa a **Tasks API** do MediaPipe (mp.tasks) — a API atual, já que o pacote
recente removeu o antigo `mediapipe.solutions`.

O Pose Landmarker devolve 33 landmarks do corpo. Usamos:
  - nariz (0), orelhas (7, 8)  → posição/tamanho da cabeça
  - pulsos (15, 16) e pontas do indicador (19, 20) → posição das mãos
  - ombros (11, 12) → referência para saber se a mão está "levantada"

Heurística: consideramos "mão na cabeça" quando uma das mãos está levantada
(acima da linha dos ombros) E perto da cabeça — com a distância normalizada
pelo tamanho da cabeça (distância entre as orelhas), para funcionar tanto perto
quanto longe da webcam.

Tudo roda 100% local, na CPU. O modelo (~5 MB) é baixado automaticamente na
primeira execução.
"""

import math
import os
import urllib.request

import config


# Índices dos landmarks do Pose (padrão MediaPipe, 33 pontos).
NOSE = 0
LEFT_EYE, RIGHT_EYE = 2, 5
LEFT_EAR, RIGHT_EAR = 7, 8
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_WRIST, RIGHT_WRIST = 15, 16
LEFT_INDEX, RIGHT_INDEX = 19, 20

# Quão perto (em múltiplos da largura da cabeça) a mão precisa estar do nariz
# para contar como "na cabeça". Maior = mais sensível.
# Calibrado com dados reais: mão na cabeça dá ratio ~1.2–2.2; mão abaixada
# dá ~4.5+. 2.5 pega o gesto com folga e fica bem longe do falso positivo.
HEAD_TOUCH_RATIO = 2.5

# A mão precisa estar ACIMA da linha das orelhas (com esta folga, em múltiplos
# da largura da cabeça) para contar como "na cabeça". Isso distingue mão na
# cabeça (acima das orelhas) de mão no queixo/apoiando o rosto (abaixo delas).
# Menor/negativo = mais rígido (exige mão bem no alto).
VERTICAL_MARGIN = 0.3

# Visibilidade mínima das orelhas (referência) para confiarmos nelas.
MIN_VISIBILITY = 0.5

# Visibilidade mínima da MÃO para confiarmos na posição dela.
HAND_MIN_VISIBILITY = 0.5

# Modelo Pose Landmarker (lite) — baixado automaticamente se não existir.
MODEL_FILENAME = "pose_landmarker_lite.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)


def _dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def _ensure_model() -> str:
    """Garante que o arquivo do modelo exista localmente; baixa se preciso."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)
    if not os.path.isfile(path):
        print(f"Baixando modelo de pose ({MODEL_FILENAME}, ~5 MB)...")
        urllib.request.urlretrieve(MODEL_URL, path)
        print("  Modelo baixado.")
    return path


class HandOnHeadDetector:
    """Detecta se uma das mãos está encostada/próxima à cabeça."""

    def __init__(self):
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision
        except ImportError as exc:
            raise RuntimeError(
                'A detecção de "mão na cabeça" requer o pacote "mediapipe". '
                "Instale com: pip install mediapipe — ou desative com "
                "ENABLE_HAND_ON_HEAD = False em config.py."
            ) from exc

        self._mp = mp
        model_path = _ensure_model()

        options = mp_vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.IMAGE,  # frames independentes
            num_poses=1,
        )
        self.landmarker = mp_vision.PoseLandmarker.create_from_options(options)

    def _landmarks(self, frame):
        """Roda o Pose e retorna a lista de landmarks (ou None se sem pessoa)."""
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB, data=rgb
        )
        result = self.landmarker.detect(mp_image)
        if not result.pose_landmarks:
            return None
        return result.pose_landmarks[0]

    def neck_gap(self, frame):
        """Distância vertical olhos→ombros normalizada pela largura da cabeça.

        Serve de proxy de postura: sentado reto o "pescoço" é longo (gap
        grande); curvado/afundado a cabeça desce e o gap encolhe. Retorna None
        se não houver pessoa/landmarks confiáveis.
        """
        lm = self._landmarks(frame)
        if lm is None:
            return None
        left_ear, right_ear = lm[LEFT_EAR], lm[RIGHT_EAR]
        left_sh, right_sh = lm[LEFT_SHOULDER], lm[RIGHT_SHOULDER]
        if (left_ear.visibility <= MIN_VISIBILITY
                or right_ear.visibility <= MIN_VISIBILITY
                or left_sh.visibility <= MIN_VISIBILITY
                or right_sh.visibility <= MIN_VISIBILITY):
            return None
        head_size = _dist(left_ear, right_ear)
        if head_size <= 0.01:
            return None
        eye_y = (lm[LEFT_EYE].y + lm[RIGHT_EYE].y) / 2.0
        sh_y = (left_sh.y + right_sh.y) / 2.0
        return (sh_y - eye_y) / head_size

    def detect(self, frame) -> bool:
        """Retorna True se detectar uma mão próxima à cabeça no frame (BGR)."""
        lm = self._landmarks(frame)
        if lm is None:
            return False

        nose = lm[NOSE]
        left_ear, right_ear = lm[LEFT_EAR], lm[RIGHT_EAR]
        left_sh, right_sh = lm[LEFT_SHOULDER], lm[RIGHT_SHOULDER]

        ears_visible = (left_ear.visibility > MIN_VISIBILITY
                        and right_ear.visibility > MIN_VISIBILITY)

        # Tamanho da cabeça (escala de normalização). Se as orelhas não estão
        # visíveis, usamos um fallback baseado na largura dos ombros.
        if ears_visible:
            head_size = _dist(left_ear, right_ear)
        else:
            head_size = _dist(left_sh, right_sh) * 0.5
        if head_size <= 0.01:
            return False  # pessoa muito longe / landmarks ruins

        # Limite vertical: a mão precisa estar ACIMA disso (y menor).
        # Preferimos a linha das orelhas — mão na cabeça fica acima das orelhas
        # (rel_ear negativo), mão no queixo fica abaixo. Sem orelhas visíveis,
        # caímos para a linha dos ombros (menos preciso).
        if ears_visible:
            ear_y = (left_ear.y + right_ear.y) / 2.0
            vertical_limit = ear_y + VERTICAL_MARGIN * head_size
        else:
            vertical_limit = (left_sh.y + right_sh.y) / 2.0

        # Candidatos de "mão": pulso e ponta do indicador de cada lado.
        hand_points = [
            lm[LEFT_WRIST], lm[RIGHT_WRIST],
            lm[LEFT_INDEX], lm[RIGHT_INDEX],
        ]

        for hand in hand_points:
            if hand.visibility < HAND_MIN_VISIBILITY:
                continue
            above = hand.y < vertical_limit         # mão acima da orelha
            near = _dist(hand, nose) < HEAD_TOUCH_RATIO * head_size
            if above and near:
                return True

        return False
