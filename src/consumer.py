import os
from collections import deque

from confluent_kafka import Consumer
from pydantic import ValidationError

from src.models.zero import Zero
from src.shared.schemas import LoadSample

c = Consumer(
    {
        "bootstrap.servers": os.environ.get("REDPANDA_ADDRESS", "localhost:19092"),
        "group.id": "scorer",
        "auto.offset.reset": "earliest",
    }
)
c.subscribe(["terna.load"])

# Computed through src/scripts/calibrate_zero.py
SCALE = 865.84
THRESHOLD = 4.0
WINDOW_LEN = 96

model = Zero(scale=SCALE, threshold=THRESHOLD, window_len=WINDOW_LEN)
window = deque(maxlen=model.window_len)

try:
    while True:
        msg = c.poll(1.0)  # Timeout -> return None

        if msg is None:
            continue

        if msg.error():
            print(msg.error())
            continue

        raw = msg.value()

        try:
            print(raw)
            sample = LoadSample.model_validate_json(raw)
            window.append(sample)

            if len(window) == model.window_len:
                score = model.score(window)
                print(score)

        except ValidationError as e:
            print(f"ValidationError for sample: {raw!r}\n{e}")
            continue


finally:
    c.close()
