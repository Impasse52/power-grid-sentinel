import os

from confluent_kafka import Consumer
from pydantic import ValidationError

from src.shared.schemas import ScoreResult
from src.storage.scores_db import init_db, insert_scores, to_row


def main():
    init_db()

    c = Consumer(
        {
            "bootstrap.servers": os.environ.get("REDPANDA_ADDRESS", "localhost:19092"),
            "group.id": "archiver",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

    c.subscribe(["terna.scores"])

    try:
        while True:
            msgs = c.consume(num_messages=100, timeout=1.0)

            results = []
            for msg in msgs:
                if msg.error():
                    print(msg.error())
                    continue

                raw = msg.value()

                try:
                    if not raw:
                        continue

                    results.append(ScoreResult.model_validate_json(raw))
                except ValidationError as e:
                    print(f"ValidationError for sample: {raw!r}\n{e}")
                    continue

            if msgs:
                insert_scores([to_row(r) for r in results])
                c.commit(asynchronous=False)

    finally:
        c.close()


if __name__ == "__main__":
    main()
