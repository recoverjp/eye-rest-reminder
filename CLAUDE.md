# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é

App Python que monitora a webcam no **Windows** e dispara lembretes de bem-estar
(descanso dos olhos, água, postura, piscar, "mão na cabeça" etc.) via notificação
nativa + som. Roda em segundo plano com um ícone na bandeja. **100% local** — nada
de rede/telemetria. Distribuído como `.exe` único via GitHub Releases.

> **Windows-only por design.** Depende de `winsound`, `winreg`, WinRT
> (`windows-toasts`) e webcam nativa. Não roda em WSL. Código e UI são em
> **português (pt-BR)** — mantenha esse idioma em comentários e strings de UI.

## Comandos

```powershell
# Dependências de runtime / de build
pip install -r requirements.txt
pip install -r requirements-build.txt      # inclui o PyInstaller

# Rodar em desenvolvimento
python tray.py        # ponto de entrada real: ícone da bandeja + monitoramento
python main.py        # só o loop de monitoramento (log no terminal, sem bandeja)
python test_smoke.py  # teste manual rápido: abre a webcam e checa o detector

# Gerar o .exe (arquivo único) — saída em dist\eye-rest-reminder.exe
python -m PyInstaller eye-rest-reminder.spec --noconfirm
# ou: build.bat

# Publicar uma release (o GitHub Actions compila e anexa o .exe sozinho)
git tag vX.Y.Z
git push origin vX.Y.Z
```

**Não há suíte de testes automatizada** (sem pytest). `test_smoke.py` é um script
manual; a calibração de thresholds foi feita com scripts descartáveis de
diagnóstico (não versionados). Ao mexer em detecção, valide com dados reais da
webcam antes de fixar números.

## Arquitetura

**Ponto de entrada = `tray.py`, não `main.py`.** `tray.py` roda o ícone do
`pystray` na **thread principal** (exigência do pystray no Windows) e executa
`main.run(...)` numa **thread daemon**. Coordenação por `threading.Event`:
`stop_event` (encerrar) e `calibrate_posture` (sinaliza o loop para salvar a
baseline de postura). Antes de qualquer import pesado, `tray.py` chama
`paths.setup_frozen_io()`.

**Dualidade código-fonte × `.exe` gira em torno de `paths.py`.** Toda gravação
persistente (`settings.json`, `stats.json`, modelos `*.task`) passa por
`paths.data_file()`. Rodando pelo fonte, isso é a pasta do projeto; empacotado
(`sys.frozen`), é `%LOCALAPPDATA%\eye-rest-reminder\` — senão os arquivos
sumiriam com a pasta temporária do PyInstaller. `setup_frozen_io()` redireciona
`stdout/stderr` para um log quando não há console (no `.exe` sem terminal, um
`print()` com `sys.stdout=None` derrubaria o app). **Nunca** grave via
`__file__`; sempre `paths.data_file()`.

**Duas camadas de configuração, não confundir:**
- `config.py` — constantes ajustáveis no código (tempos, thresholds, títulos/
  mensagens). Fonte da verdade dos *valores*.
- `settings.py` (`settings.json`) — liga/desliga cada recurso em tempo real pelo
  menu da bandeja, + valores não-booleanos (`posture_baseline`, `asked_autostart`).
  `FEATURES` define os toggles e seus rótulos. **Ao adicionar um toggle, inclua a
  chave em `FEATURES`**; `load()` só lê do disco chaves presentes em `_DEFAULTS`.

**Loop principal (`main.run`)** — o coração fica em `main.py`:
- **Cortesia com a câmera:** abre (`_open_camera`) e **libera** a webcam a *cada*
  ciclo (padrão 10s), para que Meet/Zoom possam usá-la; se estiver ocupada, a
  checagem é pulada. Não mantenha a câmera aberta entre ciclos.
- **Só `cv2.CAP_DSHOW`, nunca fallback para o backend padrão (MSMF).** Medido em
  23/09/2026: cada abertura via MSMF vaza ~144 MB no serviço FrameServer do
  Windows (DSHOW: zero), e o MSMF abre justamente quando a câmera já está em uso.
  Isso inflou o FrameServer até 21 GB e travou o PC. Câmera ocupada = pular ciclo.
- **Instância única** via mutex nomeado (`main.acquire_single_instance()`),
  chamado em `tray.run_tray()` e `main.main()`. Duas cópias disputavam a câmera.
- Detectores opcionais (MediaPipe) são carregados **uma vez no início**,
  independente do toggle; o uso por ciclo é gated por `enabled(key, fallback)`.
  Se o `mediapipe` faltar, o recurso se autodesativa sem derrubar o resto.
- Timers usam `time.monotonic()` (imunes a mudança de relógio); `datetime` só
  para exibição.
- `stats.py` (`stats.json`) acumula tempo de tela + contadores do dia, com
  rollover automático na virada do dia.

**Detecção (todos expõem métodos que recebem um frame BGR do OpenCV):**
- `detector.py` — presença de rosto/pessoa. `create_detector()` lê
  `config.DETECTOR`: `"haar"` (padrão, Haar Cascade do OpenCV, leve) ou `"yolo"`
  (opcional, exige `ultralytics`/PyTorch, ~2,5 GB — excluído do `.exe`).
- `gesture.py` — MediaPipe **Pose** Landmarker: `detect()` (mão na cabeça) e
  `neck_gap()` (proxy de postura). A distinção mão-na-cabeça × mão-no-queixo vem
  da regra "acima da linha das orelhas" + normalização pelo tamanho da cabeça.
- `eyes.py` — MediaPipe **Face** Landmarker (blendshapes): `analyze()` devolve
  presença, `blink`, `eyes_closed` e `face_width` numa única inferência.
- Usa a **Tasks API** do MediaPipe (`mp.tasks`), **não** o antigo `mp.solutions`
  (removido nas versões recentes). Modelos `.task` são baixados sob demanda.

**Notificações (`notifier.py`)** — cadeia de fallback: `windows-toasts` (WinRT,
não acumula ícone na bandeja) → `plyer` → `win10toast` → `print`. Som via
`winsound`.

**Início com o Windows (`autostart.py`)** — grava/remove um valor em
`HKCU\...\Run` (por usuário, sem admin), apontando para o `.exe` (se frozen) ou
`pythonw tray.py` (se fonte). `tray.py` pergunta na 1ª execução (guardado em
`asked_autostart`) e expõe um toggle no menu que reflete o estado real do registro.

## Empacotamento

`eye-rest-reminder.spec` gera um `.exe` único a partir de `tray.py`. Dois pontos
não óbvios que **quebram silenciosamente** se removidos:
- `collect_all("mediapipe")` — traz dados + binários nativos do MediaPipe.
- `collect_data_files("cv2")` — traz os XMLs do Haar Cascade (`cv2/data/*.xml`);
  sem isso o detector padrão não carrega no `.exe`.

`.github/workflows/release.yml` compila no `windows-latest` e publica o `.exe`
nos Releases ao dar push de uma tag `v*`.

## Convenção de commits

Mensagens de commit terminam com:
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
