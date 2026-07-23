"""Detecção de rosto/presença — dois backends selecionáveis.

Escolha o backend em `config.DETECTOR`:

  "haar"  (padrão) → Haar Cascade do OpenCV. Detecta ROSTO. Não baixa nada
                     (já vem junto com o opencv-python), usa quase nenhuma CPU.
                     Ótimo para o objetivo desta app.

  "yolo"           → YOLOv8n (ultralytics). Detecta PESSOA. Mais preciso e
                     robusto, porém exige instalar PyTorch (~2,5 GB) e usa
                     mais CPU. Instale com:  pip install ultralytics

Ambos expõem o mesmo método `.detect(frame) -> bool`, então o resto do
programa (contador, alerta) não precisa saber qual está em uso.
"""

import cv2

import config


class HaarFaceDetector:
    """Detecção de rosto via Haar Cascade (OpenCV). Leve e sem downloads."""

    def __init__(self, confidence: float = config.DETECTION_CONFIDENCE):
        # `confidence` não se aplica ao Haar; mantido só por compatibilidade
        # de assinatura com o backend YOLO.
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            raise RuntimeError(
                f"Não foi possível carregar o Haar Cascade em: {cascade_path}"
            )

    def detect(self, frame) -> bool:
        """Retorna True se houver ao menos um rosto no frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),  # ignora rostos muito pequenos (ruído/fundo)
        )
        return len(faces) > 0


class YoloDetector:
    """Detecção de pessoa via YOLOv8 (ultralytics). Requer PyTorch."""

    PERSON_CLASS_ID = 0  # classe "person" no dataset COCO

    def __init__(self, model_path: str = config.YOLO_MODEL,
                 confidence: float = config.DETECTION_CONFIDENCE):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                'O backend YOLO requer o pacote "ultralytics" (e PyTorch). '
                "Instale com: pip install ultralytics — ou use "
                'DETECTOR = "haar" em config.py.'
            ) from exc
        # O modelo é baixado automaticamente na primeira execução.
        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame) -> bool:
        """Retorna True se houver uma pessoa detectada no frame."""
        results = self.model.predict(
            frame,
            conf=self.confidence,
            classes=[self.PERSON_CLASS_ID],
            verbose=False,
        )
        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                return True
        return False


def create_detector():
    """Cria o detector conforme `config.DETECTOR` ("haar" ou "yolo")."""
    backend = str(getattr(config, "DETECTOR", "haar")).lower()
    if backend == "yolo":
        return YoloDetector()
    if backend == "haar":
        return HaarFaceDetector()
    raise ValueError(
        f'DETECTOR inválido em config.py: {backend!r}. Use "haar" ou "yolo".'
    )
