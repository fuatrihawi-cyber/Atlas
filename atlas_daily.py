# ATLAS Günlük Karar v2 - gerçek Kraken BTC/EUR günlük verisi, SANAL 50 €. Gerçek para yok.
# Günde 1 kez çalıştır (10 saniye). Kayıt dosyası gerekmez: sanal hesabı START_DATE'ten baştan hesaplar.
import json, requests, pandas as pd, numpy as np

START_DATE, START_BAL = "2026-11-19", 50.0     # sanal deneyin başlangıcı
FEE = 0.0026 + 0.0005                          # Kraken ücreti + kayma (her yön)

def candles():
    r = requests.get("https://api.kraken.com/0/public/OHLC",
                     params={"pair": "XBTEUR", "interval": 1440}, timeout=20).json()
    if r["error"]: raise SystemExit(r["error"])
    k = [v for key, v in r["result"].items() if key != "last"][0]
    d = pd.DataFrame(k, columns=["t", "o", "h", "l", "c", "vw", "v", "n"]).astype(float)
    d["t"] = pd.to_datetime(d["t"], unit="s"); d = d.set_index("t")
    return d.iloc[:-1]                         # son satır devam eden gün: kullanma

def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def votes(d):
    c = d.c
    v1 = (ema(c, 20) > ema(c, 50)).astype(float)                       # Trend Takipçisi
    v2 = (c > c.rolling(200).mean()).astype(float)                     # Uzun Vade Bekçisi
    up, dn = c > c.shift(1).rolling(20).max(), c < c.shift(1).rolling(10).min()
    p, v3 = 0.0, []
    for a, b in zip(up, dn):                                           # Kırılım Avcısı
        if p == 0 and a: p = 1.0
        elif p == 1 and b: p = 0.0
        v3.append(p)
    v3 = pd.Series(v3, index=c.index)
    return v1, v2, v3

def main():
    d = candles(); v1, v2, v3 = votes(d)
    target = (v1 + v2 + v3) / 3                # 0, %33, %67 veya %100 BTC
    ret = d.c.pct_change().fillna(0)
    pos = target.shift(1).fillna(0)
    r = pos * ret - pos.diff().abs().fillna(pos.abs()) * FEE
    sl = d.index >= START_DATE
    eq = START_BAL * (1 + r[sl]).cumprod() if sl.any() else None
    bh = START_BAL * (1 + ret[sl]).cumprod() if sl.any() else None
    print(f"Son kapanan gün: {d.index[-1].date()} | BTC {d.c.iloc[-1]:,.0f} €")
    for n, v in [("Trend Takipçisi (EMA20/50)", v1), ("Uzun Vade Bekçisi (200 gün)", v2), ("Kırılım Avcısı (Donchian)", v3)]:
        print(f"  {n}: {'AL' if v.iloc[-1] else 'BEKLE (nakitte)'}")
    t = target.iloc[-1]
    print(f"\nYARIN İÇİN HEDEF: BTC %{t*100:.0f}, nakit %{(1-t)*100:.0f}")
    print(f"Dünkü hedef: BTC %{target.iloc[-2]*100:.0f}  ->  değişim: {'VAR' if abs(t-target.iloc[-2])>0.01 else 'yok, hiçbir şey yapma'}")
    if eq is not None and len(eq):
        print(f"\nSanal hesap ({START_DATE}'ten beri): {eq.iloc[-1]:.2f} € | Al-tut olsaydı: {bh.iloc[-1]:.2f} €")
    else:
        print(f"\nDeney {START_DATE} tarihinde başlayacak.")
    e = float(eq.iloc[-1]) if eq is not None and len(eq) else START_BAL
    b = float(bh.iloc[-1]) if bh is not None and len(bh) else START_BAL
    kod = {"d": str(d.index[-1].date()), "p": round(float(d.c.iloc[-1])), "v": [int(v1.iloc[-1]), int(v2.iloc[-1]), int(v3.iloc[-1])],
           "t": round(float(t), 2), "eq": round(e, 2), "bh": round(b, 2)}
    print("\nATLAS-KOD: " + json.dumps(kod))
    print("\nBu finansal tavsiye değildir. Sanal deneydir, gerçek para yok.")

if __name__ == "__main__": main()
