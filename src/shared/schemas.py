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
