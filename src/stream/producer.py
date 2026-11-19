import os
import time

import pandas as pd
from confluent_kafka import Producer

from src.shared.schemas import LoadSample, Source

SPEED = 60 / 100
replay_file = "data/processed/terna_load.parquet"
df = pd.read_parquet(replay_file)

p = Producer(
    {"bootstrap.servers": os.environ.get("REDPANDA_ADDRESS", "localhost:19092")}
)

for ts, load, forecast, is_missing in zip(
    df.index,
    df.total_load,
    df.forecast_total_load,
    df.is_missing,
):
    value = LoadSample(
        ts_utc=ts,
        load_mw=load,
        forecast_mw=forecast,
        is_missing=is_missing,
        source=Source.REPLAY,
    )

    p.produce("terna.load", key="IT", value=value.model_dump_json())
    print(f"Sent: {value}")
    p.poll(0)
    time.sleep(SPEED)

p.flush()
