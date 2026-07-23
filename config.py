"""Constantes configuráveis do eye-rest-reminder.

Ajuste os valores abaixo conforme sua necessidade.
"""

# Após quantos minutos CONTÍNUOS de rosto detectado o alerta dispara.
ALERT_AFTER_MINUTES = 60

# Se o rosto sumir por mais que este tempo (em segundos), o contador é zerado
# (considera-se que você saiu da frente do computador).
RESET_AFTER_SECONDS = 120

# Após disparar um alerta, aguarda este tempo (em minutos) antes de poder
# disparar novamente.
COOLDOWN_AFTER_ALERT_MINUTES = 10

# Índice da webcam usada pelo OpenCV (0 = webcam padrão).
WEBCAM_INDEX = 0

# ---------------------------------------------------------------------------
# Configurações de detecção / captura
# ---------------------------------------------------------------------------

# Backend de detecção:
#   "haar" (padrão) → Haar Cascade do OpenCV. Detecta ROSTO. Não baixa nada,
#                     usa quase nenhuma CPU. Recomendado para esta app.
#   "yolo"          → YOLOv8n (ultralytics). Detecta PESSOA. Mais robusto,
#                     porém exige PyTorch (~2,5 GB). Instale: pip install ultralytics
DETECTOR = "haar"

# Modelo YOLOv8 usado quando DETECTOR = "yolo". "yolov8n.pt" é o nano.
YOLO_MODEL = "yolov8n.pt"

# Confiança mínima para considerar uma detecção válida.
DETECTION_CONFIDENCE = 0.4

# Intervalo entre as verificações, em segundos.
# Como o objetivo é contar tempo em escala de minutos/horas, não é preciso
# verificar a cada segundo. 10s é bem folgado e reduz muito o uso de CPU.
# Pode aumentar à vontade (ex.: 15, 30...).
FRAME_INTERVAL_SECONDS = 10.0

# ---------------------------------------------------------------------------
# Configurações de alerta
# ---------------------------------------------------------------------------

ALERT_TITLE = "Eye Rest Reminder"
ALERT_MESSAGE = "\U0001F440 Você está há 1 hora na tela. Descanse os olhos por 5 minutos!"

# Duração (segundos) que a notificação fica na tela.
NOTIFICATION_DURATION_SECONDS = 15

# Caminho para um arquivo .wav opcional. Se None, usa um beep do winsound.
ALERT_WAV_FILE = None
