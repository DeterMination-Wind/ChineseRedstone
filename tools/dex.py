# -*- coding: utf-8 -*-
"""把编译好的类 dex 化成 classes.dex，让 mod 在 Android 版上也能加载。

用法: python tools/dex.py <stage 目录>
"""
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, '..', 'Mindustry-master', 'desktop', 'build', 'libs', 'Mindustry.jar')
STAGE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'stage')
OUT = os.path.join(ROOT, 'build', 'dex')

SDK_ROOTS = [
    os.path.join(ROOT, '..', '.tmp-ovulam-android-sdk'),
    os.path.join(ROOT, '..', 'commandlinetools-win-14742923_latest'),
    os.path.join(ROOT, '..', 'ZalithLauncher2', '.android-sdk'),
]


def find_tools():
    d8 = os.environ.get('D8')
    android_jar = os.environ.get('ANDROID_JAR')
    if d8 and android_jar and os.path.isfile(d8) and os.path.isfile(android_jar):
        return d8, android_jar

    for sdk in SDK_ROOTS:
        build_tools = os.path.join(sdk, 'build-tools')
        if not os.path.isdir(build_tools):
            continue
        versions = sorted(os.listdir(build_tools), reverse=True)
        platforms = os.path.join(sdk, 'platforms')
        if not os.path.isdir(platforms):
            continue
        jars = sorted(os.listdir(platforms), reverse=True)
        jar = next((os.path.join(platforms, v, 'android.jar') for v in jars
                    if os.path.isfile(os.path.join(platforms, v, 'android.jar'))), None)
        for version in versions:
            bat = os.path.join(build_tools, version, 'd8.bat')
            if os.path.isfile(bat) and jar:
                return bat, jar
    return None, None


def main():
    d8, android_jar = find_tools()
    if not d8:
        raise SystemExit('d8 not found; set D8 / ANDROID_JAR or install Android build-tools')

    classes = []
    for base, _, files in os.walk(STAGE):
        for name in files:
            if name.endswith('.class'):
                classes.append(os.path.join(base, name))
    if not classes:
        raise SystemExit('no .class files in ' + STAGE)

    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)

    cmd = [d8, '--release', '--min-api', '21',
           '--lib', android_jar, '--classpath', GAME,
           '--output', OUT] + classes
    print('d8: %s' % d8)
    result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit('d8 failed')

    dex = os.path.join(OUT, 'classes.dex')
    if not os.path.isfile(dex):
        raise SystemExit('d8 produced no classes.dex')
    shutil.copyfile(dex, os.path.join(STAGE, 'classes.dex'))
    print('classes.dex: %d bytes' % os.path.getsize(dex))


if __name__ == '__main__':
    main()
