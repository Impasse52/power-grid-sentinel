import time

import pandas as pd
from confluent_kafka import Producer

from shared.schemas import LoadSample, Source

SPEED = 60
filename = "data/processed/terna_load.parquet"
df = pd.read_parquet(filename)

p = Producer({"bootstrap.servers": "localhost:19092"})

for ts, load, fc, is_missing in zip(
    df.index,
    df["total_load"],
    df["forecast_total_load"],
    df["is_missing"],
):
    value = LoadSample(
        ts_utc=ts,
        load_mw=load,
        forecast_mw=fc,
        is_missing=is_missing,
        source=Source.REPLAY,
    )

    p.produce("terna.load", key="IT", value=value.model_dump_json())
    print("sent")
    p.poll(0)
    time.sleep(60)

p.flush()
