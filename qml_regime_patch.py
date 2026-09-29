#!/usr/bin/env python3
"""Align the DASHBOARD browser QML gate with the bot: 1H -> 4H regime, 0.45 -> 0.55 corr gate."""
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()

def rep(old, new, label):
    global src
    n = src.count(old)
    assert n == 1, label + ': found ' + str(n) + ' times - NOT applied'
    src = src.replace(old, new)
    print('ok:', label)

rep('const r=await fetch("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=50");',
    'const r=await fetch("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=4h&limit=100");',
    '1 fetch 4h')

rep("QML_REGIME = last>ema*1.003 ? 'LONG' : last<ema*0.997 ? 'SHORT' : 'BOTH';",
    "QML_REGIME = last>ema*1.005 ? 'LONG' : last<ema*0.995 ? 'SHORT' : 'BOTH';",
    '2 bands')

rep("QML_REGIME==='LONG' ? '🟢 BTC 1H uptrend — BULLISH QML only' :",
    "QML_REGIME==='LONG' ? '🟢 BTC 4H uptrend — BULLISH QML only' :",
    '3 label long')
rep("QML_REGIME==='SHORT' ? '🔴 BTC 1H downtrend — BEARISH QML only' : '⚪ BTC 1H mixed — both patterns';",
    "QML_REGIME==='SHORT' ? '🔴 BTC 4H downtrend — BEARISH QML only' : '⚪ BTC 4H mixed — both patterns';",
    '3b labels')

rep("if(!(rb&&Math.abs(r.corr)>=0.45)) results.push(r);",
    "if(!(rb&&Math.abs(r.corr)>=0.55)) results.push(r);",
    '4 corr gate')

rep("· direction gated by BTC 1H trend ·",
    "· direction gated by BTC 4H trend ·",
    '5 meta text')

open(f, 'w').write(src)
print('DASHBOARD QML patch OK - browser tab now matches bot: 4H regime, 0.55 gate')
