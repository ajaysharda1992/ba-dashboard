#!/usr/bin/env python3
"""QML detector health audit - counts patterns at every filter stage.
If near-misses exist -> detector is alive, market is just strict.
If even loose structure = 0 -> detector has a structural problem."""
import json, urllib.request

URL = "https://fapi.binance.com/fapi/v1/klines?symbol={}&interval=15m&limit=300"
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT",
         "AVAXUSDT","LINKUSDT","TRXUSDT","DOTUSDT","LTCUSDT","NEARUSDT","UNIUSDT",
         "ATOMUSDT","ARBUSDT","SUIUSDT","PEPEUSDT","WIFUSDT","BCHUSDT"]
S = dict(struct=0, bos=0, l5=0, recent=0, retrace=0, bounds=0, live=0, coins_with_struct=set())

def swings15(k):
    s=[]
    for i in range(2,len(k)-2):
        l=float(k[i][3]); h=float(k[i][2])
        if l<=float(k[i-1][3]) and l<=float(k[i-2][3]) and l<=float(k[i+1][3]) and l<=float(k[i+2][3]): s.append({"i":i,"t":"L","p":l})
        if h>=float(k[i-1][2]) and h>=float(k[i-2][2]) and h>=float(k[i+1][2]) and h>=float(k[i+2][2]): s.append({"i":i,"t":"H","p":h})
    return s

def audit_coin(sym):
    try:
        with urllib.request.urlopen(URL.format(sym), timeout=15) as r:
            k = json.loads(r.read().decode())
    except Exception:
        return
    if not isinstance(k, list) or len(k) < 100: return
    closed = k[:-1]
    s = swings15(closed)
    if len(s) < 8: return
    atr = sum(float(closed[i][2])-float(closed[i][3]) for i in range(len(closed)-15, len(closed)-1))/14
    if atr <= 0: return
    vavg = sum(float(x[5]) for x in closed[-21:-1])/20
    n = len(s)
    for bull in (True, False):
        for c in range(n-1, -1, -1):
            if (s[c]["t"] != ("H" if bull else "L")) or len(closed)-s[c]["i"] > 160: continue
            for bb in range(c-1, max(0,c-50), -1):
                if s[bb]["t"] != ("L" if bull else "H"): continue
                for a in range(bb-1, max(0,bb-50), -1):
                    if s[a]["t"] != ("H" if bull else "L"): continue
                    for q in range(a-1, max(0,a-50), -1):
                        if s[q]["t"] != ("L" if bull else "H"): continue
                        S["struct"] += 1; S["coins_with_struct"].add(sym)
                        if bull:
                            if not (s[bb]["p"] < s[q]["p"] - 0.3*atr): continue
                            if not (s[c]["p"] > s[a]["p"] + 0.3*atr): continue
                        else:
                            if not (s[bb]["p"] > s[q]["p"] + 0.3*atr): continue
                            if not (s[c]["p"] < s[a]["p"] - 0.3*atr): continue
                        S["bos"] += 1
                        ex = 1e18 if bull else 0; exi = -1
                        for j in range(s[c]["i"]+1, len(closed)):
                            if bull and float(closed[j][3]) < ex: ex = float(closed[j][3]); exi = j
                            if (not bull) and float(closed[j][2]) > ex: ex = float(closed[j][2]); exi = j
                        if exi < 0: continue
                        if bull and ex < s[bb]["p"]: continue
                        if (not bull) and ex > s[bb]["p"]: continue
                        S["l5"] += 1
                        if len(closed)-exi > 40: continue
                        S["recent"] += 1
                        qm = s[a]["p"]
                        if bull:
                            if ex > qm + 0.5*atr: continue
                            risk = qm - ex
                        else:
                            if ex < qm - 0.5*atr: continue
                            risk = ex - qm
                        S["retrace"] += 1
                        if risk <= 0 or risk/qm < 0.002 or risk/qm > 0.025: continue
                        S["bounds"] += 1
                        resolved = None
                        for j in range(exi, len(closed)):
                            if bull:
                                if float(closed[j][3]) <= qm-risk: resolved="SL"; break
                                if float(closed[j][2]) >= qm+2*risk: resolved="TP"; break
                            else:
                                if float(closed[j][2]) >= qm+risk: resolved="SL"; break
                                if float(closed[j][3]) <= qm-2*risk: resolved="TP"; break
                        if resolved: continue
                        S["live"] += 1

for sym in COINS:
    audit_coin(sym)

print()
print("=== QML PIPELINE AUDIT (top-20 coins, 300 x 15m candles each) ===")
print(f"1. QM structure found (5 swings in shape)     : {S[\"struct\"]}")
print(f"2. ... + BOS break confirmed                  : {S[\"bos\"]}")
print(f"3. ... + pullback extreme valid (holds level) : {S[\"l5\"]}")
print(f"4. ... + pullback within last 10h             : {S[\"recent\"]}")
print(f"5. ... + price retraced INTO the QM zone      : {S[\"retrace\"]}")
print(f"6. ... + risk bounds ok (0.2-2.5%)            : {S[\"bounds\"]}")
print(f"7. ... + still unresolved (tradable NOW)      : {S[\"live\"]}")
print(f"coins showing QM structure at all: {len(S[\"coins_with_struct\"])}")
print()
print("Reading: if stages 1-2 are healthy but 7 = 0, the detector works and")
print("patterns are dying at a specific filter (see which number drops hardest).")
print("If stage 1 = 0, the structure scanner itself needs loosening.")
