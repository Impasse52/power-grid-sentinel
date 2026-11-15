import json

from confluent_kafka import Consumer

c = Consumer(
    {
        "bootstrap.servers": "localhost:19092",
        "group.id": "test",
        "auto.offset.reset": "earliest",
    }
)

c.subscribe(["terna.load"])

while True:
    m = c.poll(1.0)
    if m is None:
        continue
    if m.error():
        print(m.error())
        continue
    print(json.loads(m.value()))
