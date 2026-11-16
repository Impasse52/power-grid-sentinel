from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.models.zero import Zero
from src.shared.schemas import LoadSample, Source


def test_valid_model():
    z = Zero(scale=2.0, threshold=10.0)
    s = z.score(
        [
            LoadSample(
                ts_utc=datetime.now(UTC),
                load_mw=100,
                forecast_mw=98,
                is_missing=False,
                source=Source.REPLAY,
            )
        ]
    )

    assert s == 1.0


def test_gap_fails():
    z = Zero(scale=2.0, threshold=10.0)

    with pytest.raises(ValidationError):
        z.score(
            [
                LoadSample(
                    ts_utc=datetime.now(UTC),
                    load_mw=100,
                    forecast_mw=98,
                    is_missing=False,
                    source=Source.REPLAY,
                ),
                LoadSample(
                    ts_utc=datetime.now(UTC),
                    load_mw=None,
                    forecast_mw=98,
                    is_missing=False,
                    source=Source.REPLAY,
                ),
            ],
        )


def test_wrong_window_len():
    with pytest.raises(ValueError):
        Zero(scale=2.0, threshold=10.0, window_len=0)


def test_readonly_attr():
    z = Zero(scale=2.0, threshold=10.0)

    with pytest.raises(AttributeError):
        z.threshold = 5
