"""Estatísticas do dia (tempo de tela + contagem de avisos), salvas em disco.

Reinicia automaticamente quando vira o dia. Usado para o "Resumo do dia".
"""

import json
import threading
from datetime import datetime

from paths import data_file


_PATH = data_file("stats.json")

# Contadores de avisos disparados no dia.
_COUNTERS = ["eye_rest", "water", "hand_on_head", "posture", "blink", "screen_distance"]


class DailyStats:
    """Acumula tempo de tela e contadores de avisos do dia atual."""

    def __init__(self):
        self._lock = threading.Lock()
        self._date = self._today()
        self._data = self._empty()
        self._load()

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _empty() -> dict:
        data = {"present_seconds": 0.0}
        for key in _COUNTERS:
            data[key] = 0
        return data

    def _load(self) -> None:
        try:
            with open(_PATH, encoding="utf-8") as f:
                disk = json.load(f)
            if disk.get("date") == self._date:
                loaded = disk.get("data", {})
                for key in self._data:
                    if key in loaded:
                        self._data[key] = loaded[key]
        except Exception:
            pass

    def _save(self) -> None:
        try:
            with open(_PATH, "w", encoding="utf-8") as f:
                json.dump({"date": self._date, "data": self._data}, f,
                          indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _rollover(self) -> None:
        today = self._today()
        if today != self._date:
            self._date = today
            self._data = self._empty()

    def add_present(self, seconds: float) -> None:
        with self._lock:
            self._rollover()
            self._data["present_seconds"] += seconds
            self._save()

    def incr(self, key: str) -> None:
        with self._lock:
            self._rollover()
            if key in self._data:
                self._data[key] += 1
                self._save()

    def summary(self) -> str:
        with self._lock:
            self._rollover()
            d = dict(self._data)
        total = int(d["present_seconds"])
        h, m = total // 3600, (total % 3600) // 60
        return (
            f"Tempo de tela hoje: {h}h{m:02d}min\n"
            f"👀 Descansos: {d['eye_rest']}  💧 Água: {d['water']}  "
            f"🧍 Postura: {d['posture']}\n"
            f"✋ Mão na cabeça: {d['hand_on_head']}  👁️ Piscar: {d['blink']}  "
            f"🔎 Perto: {d['screen_distance']}"
        )
