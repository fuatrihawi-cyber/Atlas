# Her gün GitHub Actions tarafından çalıştırılır: Kraken verisini alır, botların oylarını hesaplar, docs/data.json yazar.
import json, os, time
from atlas_daily import candles, votes, START_DATE

def main():
    d = candles(); v1, v2, v3 = votes(d)
    out = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "pair": "XBTEUR", "start": START_DATE,
           "d": [str(t.date()) for t in d.index],
           "p": [int(round(x)) for x in d.c],
           "m": [int(a) + 2 * int(b) + 4 * int(c) for a, b, c in zip(v1, v2, v3)]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "data.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("data.json yazıldı:", len(out["d"]), "gün, son gün", out["d"][-1])

if __name__ == "__main__": main()
