# -*- coding: utf-8 -*-
"""检查 jar 结构：发布包必须同时有 .class、classes.dex、mod.hjson、语言包。"""
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', '构建', 'ChineseRedstone', 'ChineseRedstone.jar')

with zipfile.ZipFile(JAR) as zf:
    names = zf.namelist()
    print('jar: %s (%d bytes)' % (JAR, os.path.getsize(JAR)))
    for n in sorted(names):
        print('  ' + n)

    required = ['mod.hjson', 'bundle_cns.properties', 'classes.dex',
                'chineseredstone/ChineseRedstoneMod.class']
    for item in required:
        print('%-46s %s' % (item, 'OK' if item in names else 'MISSING'))

    print('--- mod.hjson ---')
    print(zf.read('mod.hjson').decode('utf-8'))
    dex = zf.read('classes.dex')
    print('dex magic: %s version=%d' % (dex[:4].decode('ascii', 'replace'), int.from_bytes(dex[4:8], 'little')))
