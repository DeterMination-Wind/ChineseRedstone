# -*- coding: utf-8 -*-
"""下载上游最新（nightly）的英文与简体中文 bundle，用于补齐 v159 之后新增的键。

输出到 _work/upstream_en.properties / _work/upstream_zh.properties
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'upstream')
os.makedirs(OUT_DIR, exist_ok=True)

FILES = {
    'bundle.properties': 'core/assets/bundles/bundle.properties',
    'bundle_zh_CN.properties': 'core/assets/bundles/bundle_zh_CN.properties',
}


def fetch(path):
    cmd = ['gh', 'api',
           'repos/Anuken/Mindustry/contents/%s?ref=master' % path,
           '-H', 'Accept: application/vnd.github.raw']
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.decode('utf-8', 'replace'))
    return result.stdout


for name, path in FILES.items():
    data = fetch(path)
    target = os.path.join(OUT_DIR, name)
    with open(target, 'wb') as f:
        f.write(data)
    print('%s: %d bytes' % (target, len(data)))
