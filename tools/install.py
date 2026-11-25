# -*- coding: utf-8 -*-
"""把构建好的 jar 安装到 构建/ChineseRedstone/ 下。

用法: python tools/install.py [--dev|--release]
"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE = '--release' in sys.argv[1:]

NAME = 'ChineseRedstone.jar' if RELEASE else 'ChineseRedstone-dev.jar'
SRC = os.path.join(ROOT, 'build', NAME)
OUT_DIR = os.path.join(ROOT, '..', '构建', 'ChineseRedstone')
DST = os.path.join(OUT_DIR, NAME)

if not os.path.isfile(SRC):
    raise SystemExit('missing built jar: ' + SRC)

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, DST)
print('installed: ' + DST)
