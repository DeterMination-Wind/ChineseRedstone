import io, re, os, sys

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'Mindustry-master', 'core', 'assets', 'bundles')


def parse(path):
    r = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#') or line.lstrip().startswith('!'):
            continue
        m = re.search(r'(?<!\\)=', line)
        if not m:
            continue
        r[line[:m.start()].strip()] = line[m.start() + 1:].strip()
    return r


zh = parse(os.path.join(BASE, 'bundle_zh_CN.properties'))
en = parse(os.path.join(BASE, 'bundle.properties'))

groups = sys.argv[1].split(',')
out = io.open(os.path.join(os.path.dirname(__file__), '..', '_work', 'dump.txt'), 'w', encoding='utf-8')
for g in groups:
    out.write('\n===== %s =====\n' % g)
    for k in en:
        if (g == '*' and '.' not in k) or k.startswith(g):
            out.write('%s\n  ZH: %s\n  EN: %s\n' % (k, zh.get(k, ''), en.get(k, '')))
out.close()
print('ok')
