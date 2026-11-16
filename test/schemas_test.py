import datetime
from datetime import UTC, datetime, timezone

import pytest
from pydantic import ValidationError

from src.shared.schemas import LoadSample

T0 = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)


def sample(minutes=0, load=100.0, fc=98.0, missing=False):
    from datetime import timedelta

    return LoadSample(
        ts_utc=T0 + timedelta(minutes=minutes),
        load_mw=load,
        forecast_mw=fc,
        is_missing=missing,
        source="replay",
    )


def test_valid_roundtrip_json():
    s = sample()
    assert LoadSample.model_validate_json(s.model_dump_json()) == s
