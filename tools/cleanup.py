# -*- coding: utf-8 -*-
"""清理早期 PowerShell 5.1 按 ANSI 读取脚本时创建的乱码目录。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(ROOT)
TARGET = '构建'

for name in os.listdir(PARENT):
    path = os.path.join(PARENT, name)
    if not os.path.isdir(path):
        continue
    try:
        repaired = name.encode('gbk', 'ignore').decode('utf-8', 'ignore')
    except Exception:
        continue
    if repaired == TARGET and name != TARGET:
        print('removing mojibake dir: %r' % name)
        shutil.rmtree(path, ignore_errors=True)

print('done')
