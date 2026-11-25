# -*- coding: utf-8 -*-
"""生成吃呢瑟（雷石东直放站版）语言包。

用法: python tools/gen_bundle.py
输出: bundle_cns.properties （模组根目录）
"""
import io
import os
import re
import random
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUNDLES = os.path.join(ROOT, '..', 'Mindustry-master', 'core', 'assets', 'bundles')

from cns_data import LEX, TRANSLIT
from cns_data2 import NAME_OVERRIDE, HERO

TOKEN_RE = re.compile(r'\[\[|\\.|\{[0-9]+\}|\[[A-Za-z0-9_#]*\]')

# 音译覆盖普通词表
TERMS = dict(LEX)
TERMS.update(TRANSLIT)

# 最长优先，单次替换，不级联
GLOSSARY_RE = re.compile('|'.join(re.escape(k) for k in sorted(TERMS, key=len, reverse=True)))

# 手写条目里还留着旧词，统一到音译体系
CONSISTENCY = {
    '建筑物': '比尔丁',
    '建筑': '比尔多',
    '播放器': '普雷尔',
    '单元': '尤尼特',
    '街区': '布洛克',
    '项目': '艾特姆',
    '核心': '科尔',
    '功率': '帕瓦',
    '研究': '瑞瑟奇',
}
CONSISTENCY_RE = re.compile('|'.join(re.escape(k) for k in sorted(CONSISTENCY, key=len, reverse=True)))

# 常见双字名词：优先在复合词里硬塞一个「的」
COMPOUND_NOUNS = ('核心|范围|半径|建筑|物品|方块|单位|电力|弹药|护盾|炮塔|波次|扇区|星球|行星|科技|'
                  '资源|速度|效率|伤害|射程|防御|攻击|生命|尺寸|距离|目标|状态|效果|时间|数据|网络|'
                  '端口|版本|日志|存档|地图|语言|音量|屏幕|窗口|鼠标|键盘|模组|建造|研究|升级')
COMPOUND_RE = re.compile('(%s)(?=[\u4e00-\u9fa5])' % COMPOUND_NOUNS)

NAME_KEY_RE = re.compile(r'^(item|block|unit|liquid|status|team|planet|sector|ability)\.'
                         r'[a-z0-9\-]+\.name$')

POSSESSIVE = ('电力|物品|液体|单位|敌人|玩家|核心|建筑|方块|科技|资源|游戏|地图|服务器|武器|'
              '弹药|护盾|能量|热量|数据|逻辑|行星|防御|进攻|军队')
POSSESSIVE_RE = re.compile('(%s)的([\\u4e00-\\u9fa5]{2,4})' % POSSESSIVE)

MODIFIERS = ('高级|低级|大型|小型|巨型|超巨型|强化|基础|普通|特殊|稀有|强大|轻型|重型|机械|'
             '气动|太阳的|塑料钛|阶段布|激增|泰坦|雷神|警察|领导|硅胶')
MODIFIER_RE = re.compile('(%s)(?=[\\u4e00-\\u9fa5])' % MODIFIERS)

PLURAL_RE = re.compile(r'(\d+\s*[个只名条座台枚张块种])([\u4e00-\u9fa5]{2,4})(?=[，。、,\.!\?！？\s]|$)')


def parse(path):
    out = {}
    pending = None
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\r\n')
        if pending is not None:
            line = pending + line.lstrip()
            pending = None
        if not line.strip() or line.lstrip().startswith('#') or line.lstrip().startswith('!'):
            continue
        # 属性文件的续行：行尾单个反斜杠表示下一行继续
        if line.endswith('\\') and not line.endswith('\\\\'):
            pending = line[:-1]
            continue
        m = re.search(r'(?<!\\)=', line)
        if not m:
            continue
        out[line[:m.start()].strip()] = line[m.start() + 1:].strip()
    return out


def protect(text):
    tokens = []

    def repl(m):
        tokens.append(m.group(0))
        return '\x00%d\x00' % (len(tokens) - 1)

    return TOKEN_RE.sub(repl, text), tokens


def restore(text, tokens):
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m.group(1))], text)


def glossary(text):
    return GLOSSARY_RE.sub(lambda m: TERMS[m.group(0)], text)


def consistency(text):
    return CONSISTENCY_RE.sub(lambda m: CONSISTENCY[m.group(0)], text)


def apply_syntax(s, rng):
    # 人称：把"你"机器地翻译成敬语
    if rng.random() < 0.35:
        s = re.sub(r'你(?![们])', '您', s, count=1)

    # 情态动词的僵硬直译
    for prob, pat, rep in (
        (0.70, '无法', '不能够'),
        (0.55, '不能(?![够])', '不可以'),
        (0.30, '不会', '将不会'),
        (0.55, '可以', '能够'),
        (0.50, '需要', '需求'),
        (0.50, '所有', '所有的'),
        (0.45, '每个', '每一个'),
        (0.30, '任何', '任何的'),
        (0.20, '这个', '这个的'),
        (0.20, '那个', '那个的'),
        (0.45, '并且', '而且'),
        (0.40, '并(?![且不])', '而且'),
        (0.30, '或(?![者])', '或者'),
        (0.25, '同时', '在相同的时间'),
        (0.30, '但是', '然而但是'),
        (0.18, '所以', '因此上'),
        (0.16, '例如', '举例来说比如说'),
        (0.24, '再次', '又一次地'),
        (0.24, '立即', '立刻地'),
        (0.20, '比较', '相对地比较'),
        (0.20, '非常', '非常地'),
        (0.18, '十分', '十分地'),
        (0.45, '用于', '被使用于'),
        (0.35, '(?<![朝向])向(?![量])', '朝向'),
        (0.30, '使(?![用得])', '使得'),
        (0.25, '能够', '是有能力去'),
        (0.30, '使用', '利用'),
        (0.25, '产生', '制造出'),
        (0.25, '提供', '供给'),
        (0.20, '增加', '添加'),
        (0.20, '减少', '降低'),
        (0.20, '允许', '许可'),
        (0.20, '自动', '自动地'),
        (0.16, '一起', '一同地'),
        (0.16, '包含', '包括着'),
        (0.16, '显示', '显示出'),
    ):
        if rng.random() < prob:
            s = re.sub(pat, rep, s)

    # 名词短语倒装：A的B -> B的A （老式统计机器翻译的招牌错误）
    if rng.random() < (0.45 if len(s) <= 16 else 0.3):
        s = POSSESSIVE_RE.sub(lambda m: m.group(2) + '的' + m.group(1), s, count=1)

    # 定语后面莫名多一个"的"
    if rng.random() < 0.5:
        s = MODIFIER_RE.sub(lambda m: m.group(1) + '的', s, count=1)

    # 复合名词之间硬塞的
    short = len(s) <= 16
    if rng.random() < (0.8 if short else 0.45):
        s = COMPOUND_RE.sub(lambda m: m.group(1) + '的', s, count=2 if short else 1)

    # 量词乱换
    if rng.random() < 0.25:
        s = s.replace('一个', '一只')
    if rng.random() < 0.25:
        s = re.sub(r'(\d+)\s*个', r'\1 只', s)

    # 动词体
    if rng.random() < 0.15:
        s = s.replace('已经', '已经曾经')
    if rng.random() < 0.12:
        s = s.replace('正在', '正在当前')

    return s


def garnish(s, rng):
    """名词复数、标点与口头语：在词表替换之后执行，只做一次。"""
    if rng.random() < 0.16:
        s = PLURAL_RE.sub(lambda m: m.group(1) + m.group(2) + '们', s, count=1)
    if rng.random() < 0.10:
        s = re.sub('(单元|街区|项目|建筑物|资源|弹药|材料|技术|扇区|墙壁)(?![们的是])', r'\1们', s, count=1)

    # 半角标点 + 空格（早期机器翻译的排版指纹）
    if rng.random() < 0.38:
        s = s.replace('，', ', ')
    if rng.random() < 0.28:
        s = s.replace('。', ' . ')
    if rng.random() < 0.22:
        s = s.replace('：', ': ')
    if rng.random() < 0.30:
        s = s.replace('！', ' !')
    if rng.random() < 0.30:
        s = s.replace('？', ' ?')
    if rng.random() < 0.20:
        s = s.replace('、', ',')

    # 偶尔的口头语残留
    if rng.random() < 0.02:
        s = s.rstrip() + ' 的说'
    if rng.random() < 0.01:
        s = '注意：' + s

    return re.sub(r' {2,}', ' ', s)


def force_change(body, rng):
    """保证文本一定有可见变化，不能只换个标点就交差。"""
    m = re.search(r'[\u4e00-\u9fa5]{2}', body)
    if m:
        choice = rng.randrange(4)
        if choice == 0:
            body = body[:m.end()] + '的' + body[m.end():]
        elif choice == 1:
            body = '被' + body
        elif choice == 2:
            body = body.rstrip() + '的'
        elif re.search(r'[\u4e00-\u9fa5]$', body.rstrip()):
            body = body.rstrip() + '们'
        else:
            body = body[:m.end()] + '的' + body[m.end():]
    else:
        body = body + ' 的说'
    return body


def strip_noise(text):
    return re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', text)


def transform(key, text):
    seed = int(hashlib.sha1(key.encode('utf-8')).hexdigest()[:8], 16)
    out = text
    # 至少尝试 6 次，保证长句子不会原封不动地漏过去
    for attempt in range(6):
        rng = random.Random(seed + attempt * 7919)
        body, tokens = protect(text)
        body = apply_syntax(body, rng)
        body = glossary(body)
        body = garnish(body, rng)
        out = restore(body, tokens)
        out = re.sub(r' {2,}', ' ', out)
        if strip_noise(out) != strip_noise(text) or attempt == 5:
            break
    # 词表和规则都没命中（常见于很短的名词标签），也要硬改一下
    if strip_noise(out) == strip_noise(text):
        rng = random.Random(seed + 104729)
        body, tokens = protect(text)
        out = restore(force_change(body, rng), tokens)
    return out


def tokens_of(text):
    return sorted(TOKEN_RE.findall(text))


def load_sources():
    """v159 基线 + 上游 nightly 新增键（用官方简中补译）。

    本地 Mindustry-master 是较早的 v159 快照；新版 nightly 会追加 Target Dummy 之类的键，
    不补的话这些文本会以英文漏出来。
    """
    en = parse(os.path.join(BUNDLES, 'bundle.properties'))
    zh = parse(os.path.join(BUNDLES, 'bundle_zh_CN.properties'))

    upstream_dir = os.path.join(ROOT, 'data', 'upstream')
    upstream_en_path = os.path.join(upstream_dir, 'bundle.properties')
    upstream_zh_path = os.path.join(upstream_dir, 'bundle_zh_CN.properties')
    extra = 0
    if os.path.isfile(upstream_en_path):
        upstream_en = parse(upstream_en_path)
        upstream_zh = parse(upstream_zh_path) if os.path.isfile(upstream_zh_path) else {}
        for key, value in upstream_en.items():
            if key not in en:
                en[key] = value
                zh[key] = upstream_zh.get(key, '')
                extra += 1
    return en, zh, extra


def main():
    en, zh, extra = load_sources()

    # 英文独有键（官方简体包里没有）——手工补上，种子随机性无法覆盖
    for key in list(en):
        if key.startswith('campaign.rework.serpulo'):
            HERO[key] = ('[accent]⚠ 塞普罗的运动已经被重新工作过。[]\\n\\n'
                         '扇区的位置和困难已经被改变。您可能遭遇与旧的布局遗留下来的运动保存文件有关的问题。\\n\\n'
                         '为了一个更干净的体验,请考虑在设定中重置您的运动保存文件。')

    lines = []
    stats = {'hero': 0, 'name': 0, 'auto': 0, 'english': 0, 'hero-fallback': 0}
    for key in en:
        src = zh.get(key)
        if src is None or not src.strip():
            src = en[key]
            stats['english'] += 1
        if key in HERO and tokens_of(HERO[key].replace('\r', '').replace('\n', '\\n')) == tokens_of(src):
            value = HERO[key]
            stats['hero'] += 1
        elif key.endswith('.name') and key[:-5] in NAME_OVERRIDE:
            value = NAME_OVERRIDE[key[:-5]]
            stats['name'] += 1
        else:
            if key in HERO:
                stats['hero-fallback'] += 1
            stats['auto'] += 1
            value = transform(key, src)
        value = consistency(value)
        value = value.replace('\r', '').replace('\n', '\\n')
        lines.append('%s = %s' % (key, value))

    out_path = os.path.join(ROOT, 'bundle_cns.properties')
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')

    print('keys: %d (+%d upstream)  hero: %d  name: %d  auto: %d  english-fallback: %d  hero-fallback: %d' %
          (len(lines), extra, stats['hero'], stats['name'], stats['auto'], stats['english'], stats['hero-fallback']))
    print('written: ' + out_path)


if __name__ == '__main__':
    main()
