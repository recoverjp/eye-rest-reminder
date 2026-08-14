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

# Quantos frames descartar ao abrir a câmera (aquecimento da auto-exposição).
# A câmera é aberta e liberada a cada checagem para não travar a webcam para
# outros apps (Google Meet, Zoom…), então aquecemos um pouco a cada abertura.
CAMERA_WARMUP_FRAMES = 4

# Intervalo entre as verificações, em segundos.
# Como o objetivo é contar tempo em escala de minutos/horas, não é preciso
# verificar a cada segundo. 10s é bem folgado e reduz muito o uso de CPU.
# Pode aumentar à vontade (ex.: 15, 30...).
FRAME_INTERVAL_SECONDS = 10.0

# ---------------------------------------------------------------------------
# Lembrete de água (por tempo)
# ---------------------------------------------------------------------------

# Liga/desliga o lembrete para beber água.
ENABLE_WATER_REMINDER = True

# A cada quantos minutos de PRESENÇA no computador lembrar de beber água.
# (Só conta enquanto você está na frente da tela; se sair por um tempo, zera.)
WATER_REMINDER_MINUTES = 60

WATER_TITLE = "Beba água 💧"
WATER_MESSAGE = "💧 Você está há 1 hora sem beber água. Hidrate-se!"

# ---------------------------------------------------------------------------
# Detecção de "mão na cabeça" (opcional — requer mediapipe)
# ---------------------------------------------------------------------------

# Liga/desliga o alerta quando você leva a mão à cabeça (ex.: mania de coçar).
# Requer: pip install mediapipe  (baixa um modelo de ~5 MB na 1ª vez).
ENABLE_HAND_ON_HEAD = True

# Tempo mínimo (segundos) entre alertas de "mão na cabeça", para não repetir
# a cada verificação enquanto a mão continua lá.
HAND_ON_HEAD_COOLDOWN_SECONDS = 60

# Antes de notificar, confirma que a mão CONTINUA na cabeça por este tempo
# (segundos), re-checando a cada 1s. Filtra gestos passageiros — coçada
# rápida, ajeitar o óculos, passar a mão no cabelo. Use 0 para desativar.
HAND_ON_HEAD_CONFIRM_SECONDS = 8

# Fração das amostras da confirmação em que a mão precisa ser detectada.
# A detecção da mão na cabeça é intermitente (~50%, por oclusão), então
# exigimos uma boa parte — não todas. Menor = mais fácil confirmar.
HAND_ON_HEAD_CONFIRM_FRACTION = 0.35

HAND_ON_HEAD_TITLE = "Mão na cabeça ✋"
HAND_ON_HEAD_MESSAGE = "✋ Você está com a mão na cabeça de novo — pare de coçar! \U0001F642"

# ---------------------------------------------------------------------------
# Descanso por "olhos fechados" (opcional — requer mediapipe)
# ---------------------------------------------------------------------------

# Se você fechar os olhos por um tempo, considera como descanso e ZERA o
# contador de tempo de tela. Requer mediapipe (baixa um modelo de ~3 MB).
ENABLE_EYES_CLOSED_REST = True

# Quantos segundos com os olhos CONTINUAMENTE fechados contam como descanso.
# Um piscar normal (frações de segundo) nunca chega perto disso.
EYES_CLOSED_REST_SECONDS = 30

# Limiar dos blendshapes de piscar (0 = aberto, ~1 = fechado) acima do qual
# consideramos o olho fechado. Calibrado com dados reais: aberto fica ≤ ~0.4
# e fechado ≥ ~0.5, então 0.45 separa bem. Ajuste se necessário.
EYE_CLOSED_THRESHOLD = 0.45

# ---------------------------------------------------------------------------
# "Perto demais da tela"
# ---------------------------------------------------------------------------

ENABLE_SCREEN_DISTANCE = True
# Fração da largura do quadro ocupada pelo rosto acima da qual = perto demais.
# (Calibrável — quanto maior o rosto no quadro, mais perto você está.)
FACE_TOO_CLOSE_RATIO = 0.45
# Segundos contínuos perto demais antes de avisar (evita avisos por um movimento).
SCREEN_TOO_CLOSE_SECONDS = 15
SCREEN_DISTANCE_COOLDOWN_SECONDS = 300
SCREEN_DISTANCE_TITLE = "Perto demais da tela 🔎"
SCREEN_DISTANCE_MESSAGE = "🔎 Você está muito perto da tela. Afaste-se um pouco!"

# ---------------------------------------------------------------------------
# "Pisque mais" (olho seco) — mede a frequência de piscadas
# ---------------------------------------------------------------------------

ENABLE_BLINK_REMINDER = True
# A cada quantos minutos medir a taxa de piscadas.
BLINK_CHECK_MINUTES = 5
# Duração da medição, em segundos (segura a câmera nesse período).
BLINK_MEASURE_SECONDS = 15
# Piscadas por minuto abaixo disso = lembrar de piscar.
BLINK_RATE_MIN = 8
# Valor do blendshape eyeBlink acima do qual o olho é considerado fechado.
BLINK_EDGE_THRESHOLD = 0.45
BLINK_TITLE = "Pisque mais 👁️"
BLINK_MESSAGE = "👁️ Você está piscando pouco. Pisque algumas vezes para lubrificar os olhos!"

# ---------------------------------------------------------------------------
# Postura (requer calibração pelo menu da bandeja)
# ---------------------------------------------------------------------------

ENABLE_POSTURE = True
# Segundos contínuos curvado antes de avisar.
POSTURE_BAD_SECONDS = 20
POSTURE_COOLDOWN_SECONDS = 300
# Quanto o "pescoço" (distância olhos→ombros) pode encolher em relação à sua
# postura calibrada antes de considerar "curvado". 0.25 = 25% menor.
POSTURE_SHRINK_TOLERANCE = 0.22
POSTURE_TITLE = "Postura 🧍"
POSTURE_MESSAGE = "🧍 Você está curvando/afundando. Endireite a postura!"

# ---------------------------------------------------------------------------
# Resumo do dia
# ---------------------------------------------------------------------------

ENABLE_DAILY_SUMMARY = True

# ---------------------------------------------------------------------------
# Configurações de alerta
# ---------------------------------------------------------------------------

ALERT_TITLE = "Eye Rest Reminder"
ALERT_MESSAGE = "\U0001F440 Você está há 1 hora na tela. Descanse os olhos por 5 minutos!"

# Duração (segundos) que a notificação fica na tela.
NOTIFICATION_DURATION_SECONDS = 15

# Caminho para um arquivo .wav opcional. Se None, usa um beep do winsound.
ALERT_WAV_FILE = None
