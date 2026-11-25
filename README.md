# 吃呢瑟（ChineseRedstone）

给 Mindustry **v159** 添加一种新语言「吃呢瑟」。

它模拟的是这样一条管线：原版英文先被最早那批**非神经网络**谷歌翻译翻成中文，再经过一次「雷石东直放站」式的转发——词义选错、专有名词音译、语序崩坏、量词乱换、半角标点、"的 / 们 / 已经"到处乱加，但每个句子仍然勉强能读懂。

示例：

| 原文 | 吃呢瑟 |
| --- | --- |
| Copper | 警察 |
| Thorium | 雷神 |
| Mass Driver | 群众的驱动器 |
| Wave | 挥手 |
| Mono | 单声道 |
| Quad | 四元组 |
| Language | 舌头 |
| Volume | 体积 |
| Logic Processor | 逻辑的处理机 |
| Memory Cell | 记忆的细胞 |

## 安装

从 [Releases](https://github.com/DeterMination-Wind/ChineseRedstone/releases) 下载 `ChineseRedstone.jar`，放进 Mindustry 的 `mods/` 目录，启动游戏。

发布包同时包含桌面版用的 `.class` 和 Android 版用的 `classes.dex`，两边都能加载。

## 使用

游戏内：**设置 → 舌头 → 吃呢瑟**，然后按提示重启游戏。

语言代码是 `cns`，和原版语言一样是可切换的独立条目，不会覆盖任何现有语言；不选中它时游戏文本完全不受影响。

## 构建

```powershell
# 需要先有本地编译好的 Mindustry 桌面 jar
./build.ps1            # 本地 dev 包：0.0.0 / ChineseRedstone-dev.jar
./build.ps1 -Release   # 发布包：版本取 mod.hjson，额外用 D8 生成 classes.dex
```

产物：

- 中间文件：`build/ChineseRedstone-dev.jar` / `build/ChineseRedstone.jar`
- 交付文件：`../构建/ChineseRedstone/` 下的同名 jar

编译用本地 `Mindustry-master/desktop/build/libs/Mindustry.jar` 当 classpath，`--release 17`，只打包自己的类、`mod.hjson`、语言包和 dex。

发布包必须同时包含 `chineseredstone/ChineseRedstoneMod.class` 和根目录的 `classes.dex`：桌面版读前者，Android 版读后者。D8 默认从本机 Android SDK build-tools 里找，也可以用环境变量 `D8` / `ANDROID_JAR` 指定。

## 翻译是怎么生成的

- 底本：官方 `core/assets/bundles/bundle_zh_CN.properties`（2911 个键，和英文完全对齐）。
- `tools/cns_data.py`：中文 → 错译词表（约 700 条），最长优先、单遍替换，不会级联。
- `tools/cns_data2.py`：具体内容键的名字覆写（物品 / 方块 / 单位 / 液体，约 270 条）与手写「英雄条目」（菜单、设置、提示、核心台词，约 240 条）。
- `tools/gen_bundle.py`：保护 `{0}`、`[accent]`、`[]`、`[[`、`\n` 等标记，再做规则化的机器腔噪声（敬语"您"、情态动词直译、定语乱加"的"、名词复数加"们"、半角标点），按 key 的哈希做确定性随机种子，因此每次生成结果稳定。
- `tools/check_bundle.py`：校验键完整、标记占位符零丢失、无明显文本事故。

重新生成：

```powershell
python tools/gen_bundle.py
python tools/check_bundle.py
./build.ps1
```

## 实现说明（为什么不是一个普通语言包）

原版 v159 没有 `bundle_cns.properties`，`I18NBundle` 会静默回退到英文根 bundle。如果按常规把 `bundle_cns.properties` 放进 mod 的 `bundles/` 目录，Mindustry 会在语言匹配时把它合并进 `Core.bundle`——但 `cns` 匹配不上，反而可能污染英语玩家的文本。

所以做法是：

1. 在 `Mod` 构造函数里把 `Locale("cns")` 插进 `Vars.locales`（这个时机早于 `UI` 构建，语言列表才能读到），并向 `LanguageDialog.displayNames` 注册显示名「吃呢瑟」。
2. 只在 `Core.settings` 里的 `locale` 等于 `cns` 时，把 jar 根目录的 `bundle_cns.properties` 手动灌进 `Core.bundle.getProperties()`。
3. 其余语言下不做任何事。

## 已知限制

- 只针对 v159 的键表；游戏更新后可能缺键（缺的键会显示成 `???key???`）。
- 这是纯文本 mod，不带贴图、不带内容，单位/方块图标仍是原版。
- 切换语言需要重启游戏，这是原版机制。
