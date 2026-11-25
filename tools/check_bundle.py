# -*- coding: utf-8 -*-
"""校验生成的 bundle：标记/占位符是否完整、有无明显文本事故。"""
import io, re, os, collections
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUNDLES = os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles')
TOKEN_RE = re.compile(r'\[\[|\\.|\{[0-9]+\}|\[[A-Za-z0-9_#]*\]')

sys.path.insert(0, HERE)
import importlib.util as _u
_spec = _u.spec_from_file_location('gb', os.path.join(HERE, 'gen_bundle.py'))
_gb = _u.module_from_spec(_spec)
_spec.loader.exec_module(_gb)
parse = _gb.parse


en, zh, extra = _gb.load_sources()
cns = parse(os.path.join(ROOT, 'bundle_cns.properties'))

print('keys en=%d (+%d upstream) cns=%d' % (len(en), extra, len(cns)))
missing = [k for k in en if k not in cns]
extra = [k for k in cns if k not in en]
print('missing keys:', missing[:10], 'extra:', extra[:10])

bad = []
for k in en:
    src = zh.get(k, en[k])
    a = collections.Counter(TOKEN_RE.findall(src))
    b = collections.Counter(TOKEN_RE.findall(cns.get(k, '')))
    if a != b:
        bad.append((k, dict(a), dict(b)))
print('token mismatches:', len(bad))
for x in bad[:15]:
    print(x)

# 文本事故：连续重复词、空值
issues = []
for k, v in cns.items():
    if not v.strip():
        issues.append((k, 'EMPTY'))
    for m in re.finditer(r'([\u4e00-\u9fa5]{2})\1', v):
        issues.append((k, 'DUP:' + m.group(0)))
print('text issues:', len(issues))
for x in issues[:20]:
    print(x)

# 统计未被改动的长句比例
from importlib import util
spec = util.spec_from_file_location('gb', os.path.join(HERE, 'gen_bundle.py'))
gb = util.module_from_spec(spec)
spec.loader.exec_module(gb)
same = 0
total = 0
for k in en:
    if k in gb.HERO or (k.endswith('.name') and k[:-5] in gb.NAME_OVERRIDE):
        continue
    src = zh.get(k, en[k])
    if len(src) < 10:
        continue
    total += 1
    if cns.get(k) == src:
        same += 1
print('long keys unchanged: %d / %d (%.1f%%)' % (same, total, 100.0 * same / max(total, 1)))
