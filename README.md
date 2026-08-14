# 👀 eye-rest-reminder

![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/plataforma-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/licença-MIT-3fbf6f)
![Local](https://img.shields.io/badge/privacidade-100%25%20local-8a2be2)

Aplicação Python que monitora sua webcam e avisa para **descansar os olhos**
após **1 hora contínua** em frente ao computador.

Usa detecção de rosto na webcam para saber se você está à frente do PC,
conta o tempo contínuo de uso e dispara uma **notificação nativa do Windows**
+ **som de alerta** quando você passa do limite.

![Preview do alerta em ação](assets/preview.png)

---

## ⬇️ Baixar (sem instalar nada)

Não quer mexer com Python? Baixe o executável pronto:

1. Vá em **[Releases](../../releases)** e baixe o `eye-rest-reminder.exe` da
   versão mais recente.
2. Dê **duplo-clique**. Não abre janela nenhuma — aparece só um **ícone de olho**
   na bandeja do Windows (perto do relógio, talvez atrás da setinha **^**).
3. Clique com o **botão direito** nesse ícone para ligar/desligar recursos, ver
   o resumo do dia ou sair.

> - **Windows apenas.** É um `.exe` único, sem instalação.
> - **A 1ª abertura demora alguns segundos** (ele se descompacta) e, se você usar
>   os recursos de mão na cabeça / postura / piscar, baixa uns ~8 MB de modelos
>   do MediaPipe na primeira vez.
> - O **Windows SmartScreen** pode avisar que é de "editor desconhecido" (o `.exe`
>   não é assinado). Clique em **Mais informações → Executar assim mesmo**.
> - Suas configurações e estatísticas ficam em
>   `%LOCALAPPDATA%\eye-rest-reminder\`.

**Iniciar junto com o Windows?** Na **primeira vez** que você abre, o app já
**pergunta** se quer isso. Você também pode ligar/desligar quando quiser pelo
menu da bandeja (**botão direito → Iniciar com o Windows**).

*(Prefere rodar pelo código-fonte? Veja [Instalação](#instalação) mais abaixo.)*

---

## 🔒 Privacidade

Todo o processamento é **100% local, na sua máquina**. A aplicação apenas lê o
frame da webcam na memória, roda a detecção e o descarta. **Nenhuma imagem é
salva em disco, e nada é enviado para a internet.** Não há servidores, telemetria
ou upload de qualquer tipo.

---

## Como funciona

- Captura um frame da webcam a cada 10 segundos (ajustável).
- **Não trava a câmera:** abre a webcam só por um instante a cada checagem e
  **libera em seguida**, então outros apps (Google Meet, Zoom…) podem usar a
  câmera normalmente — nesses momentos o app apenas pula a checagem. (Efeito
  colateral: o LED da webcam pisca brevemente a cada checagem.)
- Detecta se há um **rosto** no frame.
- Conta o tempo **contínuo** em que você está detectado.
- Ao atingir **60 minutos contínuos** → dispara o alerta.
- Se você sumir por mais de **2 minutos** → o contador é **zerado**
  (considera que você saiu).
- Após um alerta, aguarda **10 minutos** antes de poder alertar de novo.
- 💧 **Lembrete de água:** a cada **1 hora** de presença na tela, também avisa
  para você beber água (por tempo, não por detecção). Se você sair por um
  tempo, o timer reinicia.
- 🔎 **Perto demais da tela:** avisa se o seu rosto fica grande demais no quadro
  (você se aproximou muito da tela) por alguns segundos.
- 👁️ **Pisque mais (olho seco):** a cada poucos minutos, mede sua **frequência
  de piscadas** por ~15 s; se você estiver piscando pouco (staring), lembra de
  piscar.
- 🧍 **Postura:** avisa se você **curvar/afundar** por um tempo. Precisa
  **calibrar** antes (menu da bandeja → *Calibrar postura*, sentado reto).
- 📊 **Resumo do dia:** pelo menu da bandeja, veja tempo de tela e quantos
  avisos de cada tipo aconteceram hoje.

### 🖐️ Bônus: alerta de "mão na cabeça" (opcional)

Além do lembrete de descanso, a app pode te avisar sempre que você levar a
**mão à cabeça** — útil, por exemplo, pra quebrar a mania de ficar coçando a
cabeça. Usa o **MediaPipe** (Google) para achar os pontos do corpo (mãos +
cabeça) e detecta quando uma mão sobe até perto da cabeça.

- Ligado/desligado por `ENABLE_HAND_ON_HEAD` em [config.py](config.py).
- **Distingue mão na cabeça de mão no queixo:** exige que a mão esteja *acima
  da linha das orelhas*, então apoiar o rosto na mão (queixo) **não** dispara.
- **Anti-falso-positivo:** ao detectar a mão, ele **confirma por alguns
  segundos** (`HAND_ON_HEAD_CONFIRM_SECONDS`, padrão 8 s) antes de avisar. Só
  dispara se a mão for detectada em boa parte da janela
  (`HAND_ON_HEAD_CONFIRM_FRACTION`) — assim uma coçada rápida ou ajeitar o
  óculos **não** alerta; só um gesto sustentado dispara.
- Tem um *cooldown* (`HAND_ON_HEAD_COOLDOWN_SECONDS`, padrão 60 s) pra não
  repetir o aviso enquanto a mão continua lá.
- Também roda **100% local**. Baixa um modelo de ~5 MB na primeira execução.
- Se o `mediapipe` não estiver instalado, o recurso simplesmente se desativa
  (sem derrubar a app) — o lembrete de descanso continua normal.

> **📷 Dica de enquadramento:** para a detecção funcionar bem, a webcam precisa
> enxergar a mão quando ela sobe até a cabeça. Deixe a câmera na altura dos
> olhos com um bom espaço acima da cabeça (uns 20-30% do quadro). Se a câmera
> estiver muito fechada no rosto, a mão sai do quadro ao subir e a detecção
> fica instável.

### 😴 Descanso por olhos fechados (opcional)

Se você **fechar os olhos por um tempo** (descanso real, cochilo), a app
considera isso um descanso e **zera o contador de tempo de tela** — afinal,
com os olhos fechados você não está forçando a vista.

- Usa o **MediaPipe Face Landmarker** (blendshapes `eyeBlink`) para saber se os
  olhos estão fechados. Roda **100% local** (modelo de ~3 MB baixado na 1ª vez).
- Ligado/desligado por `ENABLE_EYES_CLOSED_REST` em [config.py](config.py).
- Só conta como descanso se os olhos ficarem fechados por
  `EYES_CLOSED_REST_SECONDS` (padrão 30 s) **contínuos** — um piscar normal
  nunca chega perto disso.
- O limiar `EYE_CLOSED_THRESHOLD` (padrão 0.45) define a partir de que ponto o
  olho é considerado fechado. Se não estiver disparando, tente abaixá-lo (ex.:
  0.4); se disparar à toa, aumente.

### Detector: Haar (padrão) ou YOLO

Por padrão a app usa o **Haar Cascade do OpenCV** para detecção de rosto — é
**leve, não baixa nada** (já vem no `opencv-python`) e usa quase nenhuma CPU.
Ideal para rodar o dia inteiro em segundo plano.

Se preferir, existe um backend alternativo com **YOLOv8n** (detecta *pessoa*,
mais robusto, porém exige instalar o PyTorch, ~2,5 GB). Para trocar, edite
`DETECTOR` em [config.py](config.py) para `"yolo"` e instale:
`pip install ultralytics`.

---

## Requisitos

- **Windows** (para webcam e notificações nativas — **não** rodar no WSL).
- **Python 3.10+**

---

## Instalação

Abra o **PowerShell** (ou Prompt de Comando) na pasta do projeto e rode:

```powershell
# 1. (Recomendado) crie e ative um ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt
```

> Com o detector padrão (Haar), **não há downloads adicionais** — o classificador
> já vem embutido no `opencv-python`. Basta instalar o `requirements.txt`.

---

## Execução

```powershell
python main.py
```

Para **parar**, pressione `Ctrl+C`.

---

## Log em tempo real

O terminal exibe o status a cada verificação (a cada 10 s por padrão):

```
[10:32:15] Rosto detectado — 00:45:23 contínuos
[10:32:16] Sem rosto detectado — contador pausado
...
[11:32:10] >>> ALERTA! 60 min contínuos atingidos. Descanse os olhos!
```

Quando o alerta dispara, você recebe:

- 🔔 **Notificação popup** do Windows (via `windows-toasts` / WinRT — aparece na
  Central de Ações **sem** deixar ícone acumulado na bandeja do sistema).
- 🔊 **Som de alerta** (beep, ou um `.wav` se você configurar).
- Mensagem: *"👀 Você está há 1 hora na tela. Descanse os olhos por 5 minutos!"*

---

## 🎛️ Controle pela bandeja do sistema

Ao iniciar (pelo `iniciar-silencioso.vbs` ou `iniciar.bat`), aparece um **ícone
de olho** na bandeja do Windows (perto do relógio — pode estar atrás da setinha
**^** de ícones ocultos). **Clique com o botão direito** nele para:

- ✅ **Ligar/desligar cada recurso** em tempo real (descanso dos olhos, mão na
  cabeça, olhos fechados = descanso, lembrete de água, perto demais, piscar,
  postura) — as escolhas ficam salvas em `settings.json`.
- 🧍 **Calibrar postura (sente reto)** — salva sua postura de referência para o
  aviso de postura funcionar.
- 📊 **Resumo do dia** — mostra tempo de tela e contagem de avisos de hoje.
- 🚀 **Iniciar com o Windows** — liga/desliga o início automático no login (via
  registro do usuário, sem admin). Na 1ª execução o app já pergunta se você quer.
- **Sair** — encerra o app de forma limpa (não precisa mais do Gerenciador de
  Tarefas).

> Os *tempos* (1h, 30s, etc.) continuam em [config.py](config.py); o menu da
> bandeja controla o que fica **ligado/desligado**.

---

## Configuração

Todas as constantes ficam em [config.py](config.py) e são fáceis de ajustar:

| Constante | Padrão | Descrição |
|---|---|---|
| `ALERT_AFTER_MINUTES` | `60` | Minutos contínuos até o alerta |
| `RESET_AFTER_SECONDS` | `120` | Segundos sem rosto para zerar o contador |
| `ENABLE_WATER_REMINDER` | `True` | Liga o lembrete de beber água |
| `WATER_REMINDER_MINUTES` | `60` | Minutos de presença até lembrar de beber água |
| `ENABLE_SCREEN_DISTANCE` | `True` | Liga o aviso de "perto demais da tela" |
| `FACE_TOO_CLOSE_RATIO` | `0.45` | Largura do rosto/quadro acima da qual = perto demais |
| `ENABLE_BLINK_REMINDER` | `True` | Liga o lembrete de piscar |
| `BLINK_CHECK_MINUTES` | `5` | A cada quantos min medir a taxa de piscadas |
| `BLINK_RATE_MIN` | `8` | Piscadas/min abaixo disso = lembrar de piscar |
| `ENABLE_POSTURE` | `True` | Liga o aviso de postura (requer calibrar) |
| `POSTURE_SHRINK_TOLERANCE` | `0.22` | Quanto o "pescoço" pode encolher antes de avisar |
| `ENABLE_DAILY_SUMMARY` | `True` | Resumo do dia disponível no menu da bandeja |
| `ENABLE_EYES_CLOSED_REST` | `True` | Trata olhos fechados por um tempo como descanso |
| `EYES_CLOSED_REST_SECONDS` | `30` | Segundos de olhos fechados que contam como descanso |
| `EYE_CLOSED_THRESHOLD` | `0.45` | Limiar do blendshape para considerar o olho fechado |
| `COOLDOWN_AFTER_ALERT_MINUTES` | `10` | Espera antes de poder alertar de novo |
| `WEBCAM_INDEX` | `0` | Índice da webcam (0 = padrão) |
| `ENABLE_HAND_ON_HEAD` | `True` | Liga o alerta de "mão na cabeça" (requer mediapipe) |
| `HAND_ON_HEAD_CONFIRM_SECONDS` | `8` | Janela de confirmação antes de avisar (filtra coçada rápida) |
| `HAND_ON_HEAD_CONFIRM_FRACTION` | `0.35` | Fração da janela em que a mão precisa ser detectada |
| `HAND_ON_HEAD_COOLDOWN_SECONDS` | `60` | Espera entre alertas de "mão na cabeça" |
| `DETECTOR` | `"haar"` | Backend de detecção: `"haar"` (leve) ou `"yolo"` |
| `YOLO_MODEL` | `yolov8n.pt` | Modelo usado quando `DETECTOR = "yolo"` |
| `DETECTION_CONFIDENCE` | `0.4` | Confiança mínima (usada só no YOLO) |
| `FRAME_INTERVAL_SECONDS` | `10.0` | Intervalo entre verificações (segundos) |
| `ALERT_WAV_FILE` | `None` | Caminho de um `.wav` de alerta (opcional) |

---

## Estrutura de arquivos

```
eye-rest-reminder/
  tray.py                  ← ícone da bandeja + menu (ponto de entrada)
  main.py                  ← loop principal de monitoramento
  settings.py              ← toggles ligados/desligados (salvos em settings.json)
  stats.py                 ← estatísticas do dia (resumo)
  detector.py              ← detecção de rosto (Haar) ou pessoa (YOLO)
  gesture.py               ← detecção de "mão na cabeça" (MediaPipe)
  eyes.py                  ← detecção de "olhos fechados" (MediaPipe)
  notifier.py              ← notificação Windows + som
  config.py                ← constantes configuráveis (tempos)
  paths.py                 ← pasta de dados gravável (funciona no .exe também)
  autostart.py             ← liga/desliga início com o Windows (registro HKCU)
  test_smoke.py            ← teste rápido de webcam + detector
  iniciar.bat              ← atalho: inicia mostrando o log
  iniciar-silencioso.vbs   ← atalho: inicia em segundo plano (sem janela)
  build.bat                ← gera o .exe localmente (PyInstaller)
  eye-rest-reminder.spec   ← receita do PyInstaller para o .exe
  assets/                  ← ícone (.ico), imagem de preview
  requirements.txt         ← dependências de runtime
  requirements-build.txt   ← dependências para gerar o .exe
  README.md
```

---

## Atalhos de inicialização

- **[iniciar.bat](iniciar.bat)** — duplo clique abre uma janela com o **log em
  tempo real** (e o ícone na bandeja). Para parar: menu da bandeja → **Sair**,
  ou feche a janela.
- **[iniciar-silencioso.vbs](iniciar-silencioso.vbs)** — duplo clique inicia em
  **segundo plano, sem janela** (via `pythonw`), com o ícone na bandeja. Para
  parar: menu da bandeja → **Sair**.

### Iniciar junto com o Windows (opcional)

O jeito mais fácil é pelo **menu da bandeja → "Iniciar com o Windows"** (funciona
tanto no `.exe` quanto rodando pelo código-fonte). Ele cria/remove um registro em
`HKCU\...\Run` — por usuário, sem admin.

Alternativa manual (atalho): pressione `Win + R`, digite `shell:startup`, Enter, e
crie ali um **atalho** para o `iniciar-silencioso.vbs`. Para desativar, apague o
atalho dessa pasta (ou use o Gerenciador de Tarefas → **Aplicativos de
inicialização**).

---

## 🛠️ Gerar o executável (.exe) você mesmo

O `.exe` publicado nos [Releases](../../releases) é gerado com o
**[PyInstaller](https://pyinstaller.org/)**. Para gerar por conta própria:

```powershell
# na pasta do projeto
python -m pip install -r requirements-build.txt
python -m PyInstaller eye-rest-reminder.spec --noconfirm
```

Ou simplesmente dê **duplo-clique no [build.bat](build.bat)**. O resultado sai
em `dist\eye-rest-reminder.exe`.

> O `.exe` fica grande (~300 MB) porque embute o Python, o OpenCV e o MediaPipe.
> A receita ([eye-rest-reminder.spec](eye-rest-reminder.spec)) já exclui o
> PyTorch/YOLO para não inflar ainda mais.

### Publicação automática (mantenedores)

O repositório tem um workflow do **GitHub Actions**
([.github/workflows/release.yml](.github/workflows/release.yml)) que compila o
`.exe` no Windows e o publica nos Releases automaticamente. Basta criar uma tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

---

## Solução de problemas

- **"não foi possível abrir a webcam"** — verifique se a webcam está conectada
  e se nenhum outro programa (Zoom, Teams, etc.) está usando-a. Tente outro
  valor em `WEBCAM_INDEX` (0, 1, 2...).
- **Notificação não aparece** — o Windows pode estar em modo "Não perturbe" /
  "Assistente de foco". Verifique também as permissões de notificação do app.
- **Sem som** — confirme o volume do sistema; ou configure um arquivo `.wav`
  em `ALERT_WAV_FILE`.

---

## Licença

Distribuído sob a licença **MIT** — veja o arquivo [LICENSE](LICENSE).
