import os
from collections import deque

from confluent_kafka import Consumer, Producer
from pydantic import ValidationError

from src.models.zero import Zero
from src.shared.schemas import LoadSample, ScoreResult

c = Consumer(
    {
        "bootstrap.servers": os.environ.get("REDPANDA_ADDRESS", "localhost:19092"),
        "group.id": "scorer",
        "auto.offset.reset": "earliest",
    }
)
c.subscribe(["terna.load"])

p = Producer(
    {"bootstrap.servers": os.environ.get("REDPANDA_ADDRESS", "localhost:19092")}
)

# Computed through src/scripts/calibrate_zero.py
SCALE = 865.84
THRESHOLD = 4.0
WINDOW_LEN = 3  # 96

model = Zero(scale=SCALE, threshold=THRESHOLD, window_len=WINDOW_LEN)
window = deque(maxlen=model.window_len)

try:
    while True:
        msg = c.poll(1.0)  # Timeout -> return None

        if msg is None:
            print(msg)
            continue

        if msg.error():
            print(msg.error())
            continue

        raw = msg.value()

        try:
            sample = LoadSample.model_validate_json(raw)
        except ValidationError as e:
            print(f"ValidationError for sample: {raw!r}\n{e}")
            break

        window.append(sample)

        if len(window) == model.window_len:
            score = model.score(window)
            try:
                score_res = ScoreResult(
                    ts_utc=sample.ts_utc,
                    load_mw=sample.load_mw,
                    forecast_mw=sample.forecast_mw,
                    is_missing=sample.is_missing,
                    model_version=model.version,
                    score=score,
                    threshold=model.threshold,
                    is_anomaly=score > model.threshold,
                )
                print(f"Producing score: {score_res}")

                p.produce("terna.scores", key="IT", value=score_res.model_dump_json())
                p.poll(0)
            except ValidationError as e:
                print(f"ValidationError for sample: {raw!r}\n{e}")

        else:
            print(f"Window is {len(window)} < {model.window_len}; skipping")

finally:
    p.flush()
    c.close()
