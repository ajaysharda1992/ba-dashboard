#!/usr/bin/env python3
"""
STRUCT-GATE COMPARISON (2026-10-07) - the founder's three questions on ALREADY-LOGGED data:
  1) signals the structure engine ALLOWS: how many won vs lost?
  2) the 2-candle-close break window (broken=True): how much would it have won?
  3) how many entries would the new structure have AVOIDED - and what did they cost?
Joins this morning's 'struct' analytics events with shadow outcomes (same signal key).
Read-only. Run:  cd /root && python3 struct_compare.py
NOTE: shadow outcomes mature over ~8-12h - re-run daily for the full picture.
"""
import json

def load_outcomes():
    out = {}
    for ln in open("/root/qml_shadow_hist.jsonl"):
        ln = ln.strip()
        if not ln: continue
        try: rec = json.loads(ln)
        except Exception: continue
        A = rec.get("models", {}).get("A", {}); D = rec.get("models", {}).get("D", {})
        r = A.get("r") if A.get("filled") else D.get("r")
        if r is not None: out[rec["key"]] = float(r)
    return out

def main():
    outcome = load_outcomes()
    seen = {}
    n_events = 0
    for ln in open("/root/qml_analytics.jsonl"):
        if '"ev": "struct"' not in ln: continue
        try: e = json.loads(ln)
        except Exception: continue
        n_events += 1
        if e.get("qstatus") != "RETEST": continue
        if e["key"] not in seen: seen[e["key"]] = e   # first detection of each signal
    rows = []
    for k, e in seen.items():
        if k in outcome: rows.append(dict(e, r=outcome[k]))
    pend = len(seen) - len(rows)
    def stat(g, label):
        n = len(g)
        if not n: print(f"  {label}: none yet"); return (0,0,0.0)
        w = sum(1 for r in g if r["r"] > 0)
        ar = sum(r["r"] for r in g)/n; tr = sum(r["r"] for r in g)
        print(f"  {label}: n={n} | {w}W/{n-w}L | win%={100*w/n:.0f} | avgR={ar:+.3f} | total {tr:+.1f}R")
        return (n, w, tr)
    print(f"struct events logged: {n_events} | unique RETEST signals: {len(seen)} "
          f"| with matured outcomes: {len(rows)} | still pending: {pend}")
    print("\n=== Q1: signals the STRUCTURE engine ALLOWS vs BLOCKS ===")
    allow = [r for r in rows if r["allow"]]; block = [r for r in rows if not r["allow"]]
    stat(allow, "ALLOWED by structure gate")
    stat(block, "BLOCKED by structure gate (avoided entries)")
    print("\n=== Q2: the 2-candle-close break window (broken=True) ===")
    brk = [r for r in rows if r.get("broken")]
    stat(brk, "counter-trend window trades (protected level broken)")
    brk_a = [r for r in brk if r["allow"]]
    stat(brk_a, "  of which allowed")
    print("\n=== Q3: what the avoided entries cost (under OLD exits) ===")
    if block:
        saved = -sum(r["r"] for r in block)
        print(f"  {len(block)} trades avoided | their combined outcome {sum(r['r'] for r in block):+.1f}R"
              f" -> avoiding them 'saves' {saved:+.1f}R (negative saving = the gate rejected winners)")
    print("\n=== BONUS: head-to-head with the EMA gate (same signals) ===")
    ema_block = [r for r in rows if (r["ema_dist"] or 0) > 0.3 if r["dir"]=="SHORT"] + \
                [r for r in rows if (r["ema_dist"] or 0) < -0.3 if r["dir"]=="LONG"]
    stat(ema_block, "EMA-gate would block")
    stat([r for r in rows if r not in ema_block], "EMA-gate would allow")
    print("\n(re-run daily - outcomes mature over ~8-12h; early numbers are a preview, not the verdict)")

if __name__ == "__main__":
    main()
