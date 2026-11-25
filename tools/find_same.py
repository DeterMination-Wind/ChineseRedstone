# -*- coding: utf-8 -*-
"""列出和官方简体中文完全一致（除标点外）的条目，用来找漏网的自然中文。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES = os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles')

sys.path.insert(0, os.path.join(ROOT, 'tools'))
import importlib.util as u
spec = u.spec_from_file_location('gb', os.path.join(ROOT, 'tools', 'gen_bundle.py'))
gb = u.module_from_spec(spec)
spec.loader.exec_module(gb)

en, zh, _extra = gb.load_sources()
cn = gb.parse(os.path.join(ROOT, 'bundle_cns.properties'))


def norm(t):
    return re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', t)


same = []
for k, v in cn.items():
    src = zh.get(k, en[k])
    if norm(v) == norm(src):
        same.append((k, v))

print('identical-to-zh: %d' % len(same))
for k, v in same:
    print('%-50s %s' % (k, v))
