"""Caminhos de dados graváveis — funcionam tanto rodando pelo Python quanto
empacotado como .exe (PyInstaller).

Rodando pelo código-fonte, os arquivos (settings.json, stats.json e os modelos
do MediaPipe) ficam ao lado dos .py, como sempre. Já num .exe empacotado, o
`__file__`/`sys._MEIPASS` aponta para uma pasta temporária que o Windows apaga
ao fechar — então gravar ali faria as configurações sumirem e os modelos
baixarem toda vez. Nesse caso usamos uma pasta persistente do usuário:

    %LOCALAPPDATA%\\eye-rest-reminder\\

Também há um ajuste de stdout/stderr: no .exe "sem console" (windowed), o
Python deixa sys.stdout/sys.stderr como None, e qualquer print() quebraria o
app. `setup_frozen_io()` redireciona a saída para um arquivo de log dentro da
pasta de dados.
"""

import os
import sys


APP_NAME = "eye-rest-reminder"


def is_frozen() -> bool:
    """True quando rodando como executável empacotado (PyInstaller)."""
    return getattr(sys, "frozen", False)


def data_dir() -> str:
    """Pasta onde gravamos settings/stats/modelos. Criada se não existir.

    - Empacotado: %LOCALAPPDATA%\\eye-rest-reminder (persistente).
    - Código-fonte: a própria pasta do projeto (comportamento original).
    """
    if is_frozen():
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        path = os.path.join(base, APP_NAME)
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(path, exist_ok=True)
    return path


def data_file(filename: str) -> str:
    """Caminho completo de um arquivo dentro da pasta de dados."""
    return os.path.join(data_dir(), filename)


def setup_frozen_io() -> None:
    """No .exe sem console, manda prints para um arquivo de log (evita crash).

    Sem isso, o primeiro print() com sys.stdout=None derruba o programa.
    Não faz nada quando há um console de verdade (rodando pelo Python).
    """
    if not is_frozen():
        return
    if sys.stdout is not None and sys.stderr is not None:
        return
    try:
        log_path = data_file("eye-rest-reminder.log")
        log = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = log
        sys.stderr = log
    except Exception:
        # Último recurso: descarta a saída para não quebrar nada.
        class _Null:
            def write(self, *_a, **_k):
                return 0

            def flush(self):
                pass

        sys.stdout = _Null()
        sys.stderr = _Null()
