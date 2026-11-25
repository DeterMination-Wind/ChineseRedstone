# -*- coding: utf-8 -*-
"""按前缀抽样打印生成的文本，用于人工校对。"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse(path):
    out = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ' = ' in line:
            k, v = line.split(' = ', 1)
            out[k] = v
    return out


cn = parse(os.path.join(ROOT, 'bundle_cns.properties'))
zh = parse(os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles', 'bundle_zh_CN.properties'))

prefixes = sys.argv[1:]
for prefix in prefixes:
    keys = [k for k in cn if k.startswith(prefix)]
    print('\n===== %s (%d) =====' % (prefix, len(keys)))
    step = max(1, len(keys) // 12)
    for k in keys[::step][:12]:
        print('%-44s | %s' % (k, cn[k][:110]))
