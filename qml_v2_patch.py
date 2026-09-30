#!/usr/bin/env python3
"""QML v2 dashboard patch - REBUILT with single-line anchors (whitespace-proof).
ALL-OR-NOTHING: any mismatch aborts with nothing written."""
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()

def splice(start_marker, end_marker, new_text, label):
    global src
    a = src.count(start_marker); b = src.count(end_marker)
    assert a == 1 and b == 1, f'{label}: markers {a}/{b} - NOT applied'
    i = src.index(start_marker); j = src.index(end_marker)
    assert i < j, f'{label}: order wrong'
    src = src[:i] + new_text + src[j:]
    print('ok:', label)

def rep(old, new, label):
    global src
    n = src.count(old)
    assert n == 1, f'{label}: found {n} - NOT applied'
    src = src.replace(old, new)
    print('ok:', label)

def rep_all(old, new, expect, label):
    global src
    n = src.count(old)
    assert n == expect, f'{label}: found {n}, expected {expect} - NOT applied'
    src = src.replace(old, new)
    print('ok:', label, f'({expect} occurrences)')

# --- 1. replace detectQM15 entirely (marker splice, whitespace-proof) ---
NEW_DETECT = '''function detectQM15(k, regime){
  // QML v2: raw structure + quality score. BEAR: P1=H, P2=L, P3=H>P1, P4 CLOSE<P2. QML level=P1.
  const closed=k.slice(0,-1);
  if(closed.length<40) return null;
  const s=swings15(closed);
  if(s.length<4) return null;
  let atr=0; for(let i=closed.length-15;i<closed.length-1;i++) atr+=(+closed[i][2]-+closed[i][3]);
  atr/=14;
  if(atr<=0) return null;
  let vavg=0; for(let i=Math.max(0,closed.length-21);i<closed.length-1;i++) vavg+=+closed[i][5];
  vavg/=20;
  const cur=+closed[closed.length-1][4];
  const n=s.length, SLIP=0.001, ZONE=0.15, MAXB=96, MAXD=3.0, MAXR=0.025;
  function build(bear, i1, i2, i3, p4i){
    const P1=s[i1].p, P2=s[i2].p, P3=s[i3].p;
    const sl=bear?P3*(1+SLIP):P3*(1-SLIP);
    const tp=P2, entry=P1;
    const risk=Math.abs(entry-sl);
    if(risk<=0 || risk/entry>MAXR) return null;
    const zlo=entry-ZONE*atr, zhi=entry+ZONE*atr;
    let dead=false, touches=0;
    for(let j=p4i+1;j<closed.length;j++){
      const hh=+closed[j][2], ll=+closed[j][3], cc=+closed[j][4];
      if((bear&&cc>P3)||((!bear)&&cc<P3)){ dead=true; break; }
      if(hh>=zlo&&ll<=zhi) touches++;
    }
    if(dead) return null;
    let status;
    if(touches>=2) status='USED';
    else if(touches===1) status='RETEST';
    else {
      if(closed.length-1-p4i>MAXB) return null;
      if(Math.abs(cur-entry)>MAXD*atr) return null;
      status='ARMED';
    }
    let score=2;
    const disp=Math.abs(+closed[p4i][4]-P3)/atr;
    if(disp>=0.5) score++;
    const v=Math.max(+closed[p4i][5], +closed[s[i3].i][5]);
    const volX=vavg>0?v/vavg:0;
    if(volX>=1.2) score++;
    if(volX>=1.5) score++;
    if((regime==='SHORT'&&bear)||(regime==='LONG'&&(!bear))) score++;
    if(status==='RETEST') score++;
    const rr=Math.abs(tp-entry)/risk;
    if(rr>=2) score++;
    return {dir:bear?'SHORT':'LONG', status:status, qm:entry, p1:P1, p2:P2, p3:P3, p4:+closed[p4i][4],
            sl:sl, tp:tp, zone_lo:zlo, zone_hi:zhi, score:score, disp:+disp.toFixed(2),
            volX:+volX.toFixed(2), rr:+rr.toFixed(2), grade:score>=6?'A':'B'};
  }
  const W=30;
  for(let i1=n-1;i1>=0;i1--){
    if(s[i1].t!=='H') continue;
    const P1=s[i1].p;
    for(let i2=i1+1;i2<Math.min(n,i1+W);i2++){
      if(s[i2].t!=='L') continue;
      const P2=s[i2].p;
      for(let i3=i2+1;i3<Math.min(n,i2+W);i3++){
        if(s[i3].t!=='H'||s[i3].p<=P1) continue;
        let p4i=-1;
        for(let j=s[i3].i+1;j<closed.length;j++){ if(+closed[j][4]<P2){ p4i=j; break; } }
        if(p4i<0) continue;
        const r=build(true,i1,i2,i3,p4i);
        if(r) return r;
      }
    }
  }
  for(let i1=n-1;i1>=0;i1--){
    if(s[i1].t!=='L') continue;
    const P1=s[i1].p;
    for(let i2=i1+1;i2<Math.min(n,i1+W);i2++){
      if(s[i2].t!=='H') continue;
      const P2=s[i2].p;
      for(let i3=i2+1;i3<Math.min(n,i2+W);i3++){
        if(s[i3].t!=='L'||s[i3].p>=P1) continue;
        let p4i=-1;
        for(let j=s[i3].i+1;j<closed.length;j++){ if(+closed[j][4]>P2){ p4i=j; break; } }
        if(p4i<0) continue;
        const r=build(false,i1,i2,i3,p4i);
        if(r) return r;
      }
    }
  }
  return null;
}

'''
splice('function detectQM15(k){', 'async function fetchPairQml', NEW_DETECT, '1 detectQM15 v2')

# --- 2. pass regime into detector ---
rep('const q=detectQM15(k);', 'const q=detectQM15(k, QML_REGIME);', '2 regime arg')

# --- 3. USED filter ---
rep('let d=lastQmlHits.slice().filter(r=>!r.resolved);', "let d=lastQmlHits.slice().filter(r=>r.status!=='USED');", '3 USED filter')

# --- 4. QMLMAP hot flag: 3 variants in live file, all become RETEST ---
rep_all("hot:h.status==='AT LEVEL'", "hot:h.status==='RETEST'", 3, '4 sweep badge map (x3)')

# --- 5. liveStat: single-line return anchor ---
rep("return dist<=0.4?'AT LEVEL':dist<=1.2?'APPROACHING':dist>1.5?'MOVED':'FORMING'; }",
    "if(x.zone_lo!=null){ const lp2=LIVE_PRICES[x.sym]; if(lp2) return (lp2>=x.zone_lo&&lp2<=x.zone_hi)?'RETEST':'ARMED'; } return x.status; }", '5 liveStat zone')

# --- 6. srank ---
rep("const srank=s=>s==='AT LEVEL'?0:s==='APPROACHING'?1:s==='MOVED'?3:2;",
    "const srank=s=>s==='RETEST'?0:s==='ARMED'?1:3;", '6 srank')

# --- 7. live filter ---
rep("if(qmlFilter==='live') d=d.filter(r=>liveStat(r)==='AT LEVEL');",
    "if(qmlFilter==='live') d=d.filter(r=>liveStat(r)==='RETEST');", '7 live filter')

# --- 8. ledger log gate ---
rep("const isAtLevel = h.status==='AT LEVEL';", "const isAtLevel = h.status==='RETEST';", '8 ledger gate')

# --- 9. browser badge block: insert ARMED branch; old APPROACHING/FORMING tails become harmless dead code ---
def span_splice(start_marker, new_text, label):
    global src
    n = src.count(start_marker)
    assert n == 1, f'{label}: start found {n} - NOT applied'
    i = src.index(start_marker)
    j = src.index("</span>'", i)
    j += len("</span>'")
    src = src[:i] + new_text + src[j:]
    print('ok:', label)

span_splice("const st = stStatus==='AT LEVEL'",
    "const st = stStatus==='RETEST' ? '<span style=\"color:#2ecc71;font-weight:800;\">🔥 RETEST '+(r.score!=null?r.score+'/8':'')+'</span>' : stStatus==='ARMED' ? '<span style=\"color:#C9A227;font-weight:700;\">🟡 ARMED '+(r.score!=null?r.score+'/8':'')+'</span>'", '9 browser badges')

# --- 10. bot-tab status: same insert trick (live file has no space after emoji) ---
span_splice("const st= s.status==='AT LEVEL'",
    "const st= s.status==='RETEST' ? '<span style=\"color:#2ecc71;font-weight:800;\">🔥 RETEST '+(s.score!=null?s.score+'/8':'')+'</span>' : s.status==='ARMED' ? '<span style=\"color:#C9A227;font-weight:700;\">🟡 ARMED '+(s.score!=null?s.score+'/8':'')+'</span>'", '10 bot-tab badges')

# --- 11. bot-tab score column ---
rep("<td>${s.grade||''}</td></tr>", "<td>${s.grade||''} ${s.score!=null?s.score+'/8':''}</td></tr>", '11 score column')

# --- 12. dropdown label ---
rep('Show: tradeable now (AT LEVEL only)', 'Show: RETEST only', '12 dropdown')

open(f, 'w').write(src)
print('QML v2 dashboard patch v2 OK - all anchors matched')
