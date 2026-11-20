from datetime import UTC, datetime
from sqlite3 import connect

from src.shared.schemas import ScoreResult

DB_PATH = "data/processed/scores.db"

TABLE_INIT = """
CREATE TABLE IF NOT EXISTS scores (
    ts_utc TEXT NOT NULL,
    model_version TEXT NOT NULL,
    load_mw REAL,
    forecast_mw REAL,
    score REAL,
    threshold REAL,
    is_anomaly BOOL,
    is_missing BOOL,
    PRIMARY KEY (ts_utc, model_version)
)
"""

UPSERT = """
INSERT INTO scores (
    ts_utc, model_version, load_mw, forecast_mw,
    score, threshold, is_anomaly, is_missing
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (ts_utc, model_version) DO UPDATE SET
    load_mw     = excluded.load_mw,
    forecast_mw = excluded.forecast_mw,
    score       = excluded.score,
    threshold   = excluded.threshold,
    is_anomaly  = excluded.is_anomaly,
    is_missing  = excluded.is_missing
"""

SELECT_SCORES = """
SELECT ts_utc, model_version, load_mw, forecast_mw, score, threshold, is_anomaly, is_missing
FROM scores;
"""


def init_db():
    with connect(DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(TABLE_INIT)
        con.commit()


def insert_scores(row: list[tuple]):
    with connect(DB_PATH) as con:
        con.executemany(UPSERT, row)
        con.commit()


def read_scores():
    with connect(DB_PATH) as con:
        cur = con.execute(SELECT_SCORES)
        return cur.fetchall()


def from_row(row: tuple) -> "ScoreResult":
    return ScoreResult(
        ts_utc=datetime.fromisoformat(str(row[0])),
        model_version=row[1],
        load_mw=row[2],
        forecast_mw=row[3],
        score=row[4],
        threshold=row[5],
        is_anomaly=row[6],
        is_missing=row[7],
    )


def to_row(values: ScoreResult) -> tuple:
    return (
        values.ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        values.model_version,
        values.load_mw,
        values.forecast_mw,
        values.score,
        values.threshold,
        values.is_anomaly,
        values.is_missing,
    )


if __name__ == "__main__":
    init_db()
    insert_scores([(datetime.now(UTC), "yada:0", 5.0, 4.9, 0.15, 4, 0, 0)])
    res = read_scores()
    print(res)
    from_row(res[0])
