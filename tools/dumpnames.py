import io, re, os

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
        k = line[:m.start()].strip()
        v = line[m.start() + 1:].strip()
        r[k] = v
    return r


zh = parse(os.path.join(BASE, 'bundle_zh_CN.properties'))
en = parse(os.path.join(BASE, 'bundle.properties'))

out = io.open(os.path.join(os.path.dirname(__file__), '..', '_work', 'names.txt'), 'w', encoding='utf-8')
for pr in ['item', 'liquid', 'unit', 'status', 'block']:
    out.write('==== %s ====\n' % pr)
    for k in en:
        if k.startswith(pr + '.') and k.endswith('.name'):
            out.write('%-44s | %-28s | %s\n' % (k[:-5], zh.get(k, ''), en.get(k, '')))
out.close()
print('ok')
