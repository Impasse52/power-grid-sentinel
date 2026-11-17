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

for threshold in [3, 3.5, 4, 4.5]:
    above = test_scores[test_scores > threshold]
    days = above.index.normalize().nunique()
    print(f"soglia={threshold}: {len(above)} campioni, {days} giorni")

print(test.index.normalize().nunique())

# df["score"] = df["residual"].abs() / scale
# print(df.groupby(df.index.year)["score"].agg(["median", lambda s: s.quantile(0.99)]))

threshold = 4
above = test_scores[test_scores > threshold]
days = above.index.normalize().nunique()
print(f"soglia={threshold}: {len(above)} campioni, {days} giorni")

above.index = above.index.tz_convert("Europe/Rome")
# above.to_csv("above.csv")

print(test["residual"].groupby(test["residual"].index.hour).median() / scale)
print(test["residual"].groupby(test["residual"].index.day_of_week).median() / scale)

print(scale)
