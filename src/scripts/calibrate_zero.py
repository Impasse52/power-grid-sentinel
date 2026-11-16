import pandas as pd

CUTOFF = pd.Timestamp("2025-01-01", tz="UTC")
MAD_NORMAL_CONSISTENCY = 1.4826

df = pd.read_parquet("data/processed/terna_load.parquet")
df["residual"] = df["total_load"] - df["forecast_total_load"]

train = df[df.index < CUTOFF]
test = df[df.index >= CUTOFF]
print(len(train), len(test), df.index.min(), df.index.max())

# compute med and mad
med = train["residual"].median()
mad = (train["residual"] - med).abs().median()
scale = MAD_NORMAL_CONSISTENCY * mad
print("MAD scale:", scale, "| std:", train["residual"].std())

test_scores = test["residual"].abs() / scale
print(test_scores.quantile([0.5, 0.9, 0.99, 0.999]), test_scores.max())
