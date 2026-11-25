# -*- coding: utf-8 -*-
"""按模式生成 mod.hjson 元数据。

仓库里提交的 mod.hjson 是发布身份；本地 dev 构建用 --dev 临时改成 0.0.0 / -dev。

用法: python tools/meta.py --dev <输出文件>
      python tools/meta.py --release <输出文件>
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'mod.hjson')


def parse(text):
    pairs = []
    for line in text.splitlines():
        if ':' not in line or line.lstrip().startswith('#'):
            pairs.append((None, line))
            continue
        key, value = line.split(':', 1)
        pairs.append((key.strip(), value.strip()))
    return pairs


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('--dev', '--release'):
        raise SystemExit(__doc__)
    mode, out_path = sys.argv[1], sys.argv[2]

    pairs = parse(io.open(SOURCE, encoding='utf-8').read())
    base_name = next(v for k, v in pairs if k == 'name')
    version = next(v for k, v in pairs if k == 'version')

    if mode == '--dev':
        base_name = base_name.replace('-dev', '') + '-dev'
        version = '0.0.0'

    lines = []
    for key, value in pairs:
        if key == 'name':
            value = base_name
        elif key == 'version':
            value = version
        lines.append(value if key is None else '%s: %s' % (key, value))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines).rstrip('\n') + '\n')
    print('meta (%s): %s %s -> %s' % (mode, base_name, version, out_path))


if __name__ == '__main__':
    main()
