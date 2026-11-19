from sqlite3 import connect

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
SELECT * FROM scores;
"""


def init_db():
    with connect(DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(TABLE_INIT)
        con.commit()


def insert_scores(row: tuple):
    with connect(DB_PATH) as con:
        con.executemany(UPSERT, [row])
        con.commit()


def read_scores():
    with connect(DB_PATH) as con:
        cur = con.execute(SELECT_SCORES)
        return cur.fetchall()
