import math
from collections.abc import Sequence

from src.models.base import AnomalyModel
from src.shared.schemas import LoadSample


class Zero(AnomalyModel):
    def __init__(self, scale: float, threshold: float, window_len: int = 96):
        if not (math.isfinite(scale) and scale > 0):
            raise ValueError("scale must be finite and positive")
        if not math.isfinite(threshold):
            raise ValueError("threshold must be finite")
        if window_len < 1:
            raise ValueError("window_len must be >= 1")

        self._scale = scale
        self._threshold = threshold
        self._window_len = window_len

    @property
    def version(self) -> str:
        return "zero-residual:1"

    @property
    def window_len(self) -> int:
        return self._window_len

    @property
    def threshold(self) -> float:
        return self._threshold

    def score(self, window: Sequence[LoadSample]) -> float:
        last = window[-1]

        if last.load_mw is None or last.forecast_mw is None:
            raise ValueError("score requires at least one complete last sample")

        return abs(last.load_mw - last.forecast_mw) / self._scale
