#!/usr/bin/env python3
# Safety-patch mirror: ordering sanity in dashboard detectQM15 (keep both sides identical).
f = '/tmp/ba-dashboard/index.html'
src = open(f).read()
old = "const P1=s[i1].p, P2=s[i2].p, P3=s[i3].p;"
n = src.count(old)
assert n == 1, 'anchor found ' + str(n) + ' - NOT applied'
new = "const P1=s[i1].p, P2=s[i2].p, P3=s[i3].p;\n    if(bear&&P2>=P1) return null;\n    if((!bear)&&P2<=P1) return null;"
src = src.replace(old, new)
open(f, 'w').write(src)
print('DASHBOARD MIRROR OK - ordering check added to JS build()')
