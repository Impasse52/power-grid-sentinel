import json
import time
from glob import glob

import pandas as pd
from confluent_kafka import Producer

SPEED = 60
files = glob("data/**.csv")
df = pd.read_csv(files[0], parse_dates=["Date"])
p = Producer({"bootstrap.servers": "localhost:19092"})

for ts, load in zip(df["Date"], df["Total Load [MW]"]):
    value = json.dumps({"ts": ts.isoformat(), "load_mw": float(load)})
    p.produce("terna.load", key="IT", value=value)
    print("sent")
    p.poll(0)
    time.sleep(60)

p.flush()
