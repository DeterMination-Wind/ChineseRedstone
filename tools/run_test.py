# -*- coding: utf-8 -*-
"""在隔离的数据目录里真机启动一次 Mindustry，验证模组能加载、语言包能注入。

不碰用户真实的 %APPDATA%\\Mindustry：整个数据目录被重定向到临时目录。
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import traceback

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', '构建', 'ChineseRedstone', 'ChineseRedstone.jar')
GAME = os.path.join(ROOT, '..', 'Mindustry-master', 'desktop', 'build', 'libs', 'Mindustry.jar')
BASE = os.path.join(tempfile.gettempdir(), 'cr-run')
APPDATA = os.path.join(BASE, 'appdata')
DATA = os.path.join(APPDATA, 'Mindustry')
MODS = os.path.join(DATA, 'mods')
LOG = os.path.join(DATA, 'last_log.txt')


def write_settings(locale):
    """按 arc Settings 的二进制格式写 settings.bin（DataOutputStream）。"""
    body = struct.pack('>i', 1)
    key = 'locale'.encode('utf-8')
    body += struct.pack('>H', len(key)) + key
    body += b'\x04'
    val = locale.encode('utf-8')
    body += struct.pack('>H', len(val)) + val
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, 'settings.bin'), 'wb') as f:
        f.write(body)


shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(MODS, exist_ok=True)
shutil.copyfile(JAR, os.path.join(MODS, 'ChineseRedstone-dev.jar'))
write_settings('cns')
print('data dir: ' + DATA)

env = dict(os.environ)
env['APPDATA'] = APPDATA
env['LOCALAPPDATA'] = os.path.join(BASE, 'localappdata')
os.makedirs(env['LOCALAPPDATA'], exist_ok=True)

proc = subprocess.Popen(
    ['java', '-Xmx1G', '-jar', GAME],
    cwd=BASE, env=env,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
)

deadline = time.time() + 100
found = False
while time.time() < deadline:
    time.sleep(2)
    if os.path.exists(LOG):
        try:
            text = open(LOG, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        if '[ChineseRedstone]' in text:
            found = True
            break
    if proc.poll() is not None:
        break

time.sleep(1)
subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print('found marker: %s' % found)
if os.path.exists(LOG):
    text = open(LOG, encoding='utf-8', errors='replace').read()
    lines = text.splitlines()
    print('--- log lines mentioning ChineseRedstone / mod / error ---')
    for line in lines:
        low = line.lower()
        if 'chineseredstone' in low or 'loading mod' in low or 'mod load' in low or 'exception' in low or 'error' in low:
            print(line)
    print('--- tail ---')
    for line in lines[-25:]:
        print(line)
else:
    print('no log file was produced')
out = proc.stdout.read() if proc.stdout else b''
print('--- stdout tail ---')
print(out.decode('utf-8', 'replace')[-3000:])
