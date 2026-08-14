"""Configurações ligáveis/desligáveis em tempo real, persistidas em disco.

Os valores iniciais vêm de `config.py`; depois ficam salvos em `settings.json`
(ao lado do código) e podem ser alterados pelo menu do ícone da bandeja.
"""

import json
import os
import threading

import config


_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

# Chave interna -> (rótulo no menu, valor padrão vindo do config)
FEATURES = [
    ("eye_rest", "Descanso dos olhos (1h)", True),
    ("hand_on_head", "Alerta de mão na cabeça", config.ENABLE_HAND_ON_HEAD),
    ("eyes_closed_rest", "Olhos fechados = descanso", config.ENABLE_EYES_CLOSED_REST),
    ("water", "Lembrete de água", config.ENABLE_WATER_REMINDER),
    ("screen_distance", "Aviso de tela perto demais", config.ENABLE_SCREEN_DISTANCE),
    ("blink", "Lembrete de piscar", config.ENABLE_BLINK_REMINDER),
    ("posture", "Aviso de postura", config.ENABLE_POSTURE),
]

_DEFAULTS = {key: default for key, _label, default in FEATURES}
# Valores não-booleanos persistidos junto (ex.: calibração de postura).
_DEFAULTS["posture_baseline"] = None


class Settings:
    """Guarda os toggles em memória, com persistência em JSON (thread-safe)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._data = dict(_DEFAULTS)
        self.load()

    def load(self) -> None:
        toggle_keys = {key for key, _l, _d in FEATURES}
        try:
            with open(_PATH, encoding="utf-8") as f:
                disk = json.load(f)
            with self._lock:
                for key in _DEFAULTS:
                    if key in disk:
                        # toggles são booleanos; o resto (ex.: baseline) é cru.
                        self._data[key] = (
                            bool(disk[key]) if key in toggle_keys else disk[key]
                        )
        except FileNotFoundError:
            self.save()  # cria o arquivo na primeira vez
        except Exception:
            pass

    def save(self) -> None:
        try:
            with self._lock:
                data = dict(self._data)
            with open(_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str) -> bool:
        with self._lock:
            return bool(self._data.get(key, False))

    def set(self, key: str, value: bool) -> None:
        with self._lock:
            self._data[key] = bool(value)
        self.save()

    def toggle(self, key: str) -> bool:
        self.set(key, not self.get(key))
        return self.get(key)

    # --- valores não-booleanos (ex.: calibração de postura) ---
    def get_value(self, key: str, default=None):
        with self._lock:
            return self._data.get(key, default)

    def set_value(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = value
        self.save()
