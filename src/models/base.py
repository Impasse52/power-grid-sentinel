from abc import ABC, abstractmethod

from src.shared.schemas import LoadSample


class AnomalyModel(ABC):
    @property
    @abstractmethod
    def version(self):
        """Model version"""

    @property
    @abstractmethod
    def window_len(self):
        """Number of consecutive samples that the model gets as input"""

    @property
    @abstractmethod
    def threshold(self):
        """Threshold for anomaly detection"""

    @abstractmethod
    def score(self, window: list[LoadSample]) -> float:
        """Returns a float score for the last sample in the window."""
