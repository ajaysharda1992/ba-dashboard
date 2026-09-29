#!/usr/bin/env python3
"""One-time patch: make the dashboard's local sweep ledger MIRROR the bot book
(adds missing trades AND removes bot-sourced entries the bot no longer has)."""
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()

old = """  try{ // MERGE bot history into local ledger (add missing trades, keep existing)
    const have=new Set(SIG_HIST.map(r=>r.sym+'|'+r.dir+'|'+r.entry+'|'+r.resultR));"""
new = """  try{ // SYNC bot history with local ledger: add missing + REMOVE stale bot-sourced entries
    const botKeys=new Set(hist.map(h=>(h.sym||'').replace('USDT','')+'|'+h.dir+'|'+h.entry+'|'+h.resultR));
    SIG_HIST=SIG_HIST.filter(r=>r.sweep!=='(from bot)'||botKeys.has(r.sym+'|'+r.dir+'|'+r.entry+'|'+r.resultR));
    const have=new Set(SIG_HIST.map(r=>r.sym+'|'+r.dir+'|'+r.entry+'|'+r.resultR));"""

n = src.count(old)
assert n == 1, 'ERROR: merge block found ' + str(n) + ' times - repo file changed? Patch NOT applied.'
open(f, 'w').write(src.replace(old, new))
print('SYNC patch OK - local ledger will now mirror the bot book (adds + auto-removes)')
