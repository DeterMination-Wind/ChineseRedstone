import io, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES = os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles')


def parse(p):
    o = {}
    for l in io.open(p, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l.strip() or l.lstrip().startswith('#'):
            continue
        m = re.search(r'(?<!\\)=', l)
        if m:
            o[l[:m.start()].strip()] = l[m.start() + 1:].strip()
    return o


zh = parse(os.path.join(BUNDLES, 'bundle_zh_CN.properties'))
en = parse(os.path.join(BUNDLES, 'bundle.properties'))
cn = parse(os.path.join(ROOT, 'bundle_cns.properties'))

sel = sys.argv[1:]
o = io.open(os.path.join(ROOT, '_work', 'review.txt'), 'w', encoding='utf-8')
for s in sel:
    o.write('\n########## %s ##########\n' % s)
    for k in en:
        if k.startswith(s) and (k.endswith('.name') or k.endswith('.description')):
            o.write('%-46s | %-26s | %s\n' % (k, zh.get(k, ''), cn.get(k, '')))
o.close()
print('ok')
