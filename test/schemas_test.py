from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.shared.schemas import LoadSample, ScoreResult

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


def test_naive_timestamp_rejected():
    with pytest.raises(ValidationError):
        LoadSample(
            ts_utc=datetime(2024, 1, 1),
            load_mw=1,
            forecast_mw=1,
            is_missing=False,
            source="replay",
        )


def test_naive_timestamp_rejected_in_score():
    with pytest.raises(ValidationError):
        ScoreResult(
            ts_utc=datetime(2024, 1, 1),
            load_mw=1,
            forecast_mw=1,
            is_missing=False,
            score=0.0,
            threshold=0.0,
            is_anomaly=False,
            model_version="",
        )
