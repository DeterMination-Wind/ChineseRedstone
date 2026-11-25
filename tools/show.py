# -*- coding: utf-8 -*-
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES = os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import importlib.util as u
spec = u.spec_from_file_location('gb', os.path.join(ROOT, 'tools', 'gen_bundle.py'))
gb = u.module_from_spec(spec)
spec.loader.exec_module(gb)

zh = gb.parse(os.path.join(BUNDLES, 'bundle_zh_CN.properties'))
en = gb.parse(os.path.join(BUNDLES, 'bundle.properties'))
cn = gb.parse(os.path.join(ROOT, 'bundle_cns.properties'))
for k in sys.argv[1:]:
    print(k)
    print('  ZH: ' + zh.get(k, '<none>'))
    print('  EN: ' + en.get(k, '<none>'))
    print('  CN: ' + cn.get(k, '<none>'))
