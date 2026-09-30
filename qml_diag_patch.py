#!/usr/bin/env python3
"""QML v2 diagnostic: surface the real error message + refresh stale copy."""
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()

def rep(old, new, label):
    global src
    n = src.count(old)
    assert n == 1, f'{label}: found {n} - NOT applied'
    src = src.replace(old, new)
    print('ok:', label)

# 1. surface the actual exception message on the status line
rep("catch(e){ console.error('qml scan error', e); st.textContent='⚠️ QML scan error — retries next cycle'; }",
    "catch(e){ console.error('qml scan error', e); st.textContent='⚠️ '+(e&&e.message||e); }",
    '1 error surfacing')

# 2. stale meta text (old rules description)
old_meta = None
for cand in ["Classic 5-point QM (pts 1–5) on the 15m chart",
             "Classic 5-point QM"]:
    if cand in src:
        old_meta = cand; break
assert old_meta, 'meta anchor not found'
i = src.index(old_meta)
j = src.index('trap setups removed', i) + len('trap setups removed')
src = src[:i] + "QML v2 — raw structure detection: P1 → P2 → P3 sweep beyond P1 → P4 CLOSE beyond P2 (BOS) · 🟡 ARMED awaits retest · 🔥 RETEST = entry zone (P1 ± 0.15 ATR) · quality score /8: volume ≥1.2/1.5× · displacement ≥0.5 ATR · BTC 4H agreement · first retest · R:R ≥2 · SL beyond P3 · TP at P2 · invalid on close beyond P3" + src[j:]
print('ok: 2 meta text')

# 3. stale ledger header copy
rep("AT-LEVEL entry (limit at QM level · SL beyond pattern · TP 1:2)", "RETEST detection (entry in P1 zone · SL beyond P3 · TP at P2)", '3 ledger header')

open(f, 'w').write(src)
print('Diagnostic patch OK')
