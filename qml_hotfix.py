#!/usr/bin/env python3
# QML v2 hotfix: re-insert fetchQmlRegime (accidentally removed by the v2 splice).
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()

old = 'async function fetchPairQml(sym){'
n = src.count(old)
assert n == 1, 'anchor found ' + str(n) + ' - NOT applied'
assert 'fetchQmlRegime' not in src, 'fetchQmlRegime already exists - NOT applied'

new = "async function fetchQmlRegime(){\n  try{\n    const r=await fetch(\"https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=4h&limit=100\");\n    const k=await r.json();\n    if(Array.isArray(k)&&k.length>25){\n      const m=2/21; let ema=+k[0][4];\n      for(let i=1;i<k.length-1;i++){ ema=((+k[i][4])-ema)*m+ema; }\n      const last=+k[k.length-2][4];\n      QML_REGIME = last>ema*1.005 ? 'LONG' : last<ema*0.995 ? 'SHORT' : 'BOTH';\n    }\n  }catch(e){ QML_REGIME='BOTH'; }\n}\n\nasync function fetchPairQml(sym){"

src = src.replace(old, new)
open(f, 'w').write(src)
print('HOTFIX OK - fetchQmlRegime restored (4H regime version)')
