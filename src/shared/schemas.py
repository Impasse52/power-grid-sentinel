from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = 1


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Source(str, Enum):
    REPLAY = "replay"
    LIVE = "live"


def _check_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None or ts.utcoffset() != timedelta(0):
        raise ValueError("Timestamp must be UTC")
    return ts.astimezone(UTC)


class LoadSample(_Base):
    "Message on topic `terna.load`"

    schema_version: int = 1
    ts_utc: datetime
    load_mw: float | None = Field(ge=0.0, allow_inf_nan=False)
    forecast_mw: float | None = Field(ge=0.0, allow_inf_nan=False)
    is_missing: bool
    source: Source

    @field_validator("schema_version")
    @classmethod
    def _version(cls, value: int) -> int:
        if value != SCHEMA_VERSION:
            raise ValueError(
                f"Expected schema version: {SCHEMA_VERSION}, actual: {value}"
            )
        return value

    @field_validator("ts_utc")
    @classmethod
    def _ts(cls, value: datetime) -> datetime:
        return _check_utc(value)

    @model_validator(mode="after")
    def _coherent(self) -> "LoadSample":
        is_incomplete = self.load_mw is None or self.forecast_mw is None

        if self.is_missing != is_incomplete:
            raise ValueError(
                "is_missing can only be True if load_mw or forecast_mw are None"
            )

        return self


class ScoreRequest(_Base):
    samples: list[LoadSample] = Field(min_length=1)

    @model_validator(mode="after")
    def _consecutive(self) -> "ScoreRequest":
        for i, j in zip(self.samples, self.samples[1:]):
            if j.ts_utc - i.ts_utc != timedelta(minutes=15):
                raise ValueError("Timestamps must be consecutive with a step of 15 min")

        return self


class ScoreResponse(_Base):
    schema_version: int
    ts_utc: datetime
    score: float | None = Field(ge=0.0, allow_inf_nan=False)
    threshold: float | None = Field(ge=0.0, allow_inf_nan=False)
    is_anomaly: bool
    is_missing: bool
    model_version: str

    @field_validator("ts_utc")
    @classmethod
    def _ts(cls, value: datetime) -> datetime:
        return _check_utc(value)


class ScoreResult(ScoreResponse):
    load_mw: float | None = Field(ge=0.0, allow_inf_nan=False)
    forecast_mw: float | None = Field(ge=0.0, allow_inf_nan=False)

    @model_validator(mode="after")
    def _coherent(self) -> "ScoreResult":
        is_incomplete = self.load_mw is None or self.forecast_mw is None

        if self.is_missing != is_incomplete:
            raise ValueError(
                "is_missing can only be True if load_mw or forecast_mw are None"
            )

        return self
