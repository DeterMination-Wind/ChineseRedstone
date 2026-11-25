package chineseredstone;

import arc.Core;
import arc.files.Fi;
import arc.util.Log;
import arc.util.io.PropertiesUtils;
import mindustry.Vars;
import mindustry.mod.Mod;
import mindustry.mod.Mods;
import mindustry.ui.dialogs.LanguageDialog;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/**
 * 吃呢瑟：把原版英文经"最早的非神经网络谷歌翻译"翻成中文，再被雷石东直放站转发一次的假语言。
 *
 * 核心没有 bundle_cns.properties，I18NBundle 会静默回退到英文根 bundle，
 * 所以翻译不能放进 mod 的 bundles/ 目录（那样英语玩家也会被汉化），
 * 只能在确认当前 locale 是 cns 之后手动灌进 Core.bundle。
 */
public class ChineseRedstoneMod extends Mod{
    public static final String langCode = "cns";
    public static final String langName = "吃呢瑟";
    public static final String bundleFile = "bundle_cns.properties";

    public ChineseRedstoneMod(){
        // Mod 构造发生在 Vars.init() 末尾、UI 构建之前，此时改 Vars.locales 才会被语言列表读到
        registerLocale();
        injectBundle();
    }

    @Override
    public void init(){
        // 兜底：某些启动路径下 Core.bundle 可能在 Mod 构造之后才就绪
        injectBundle();
    }

    private void registerLocale(){
        try{
            Locale cns = new Locale(langCode);

            if(Vars.locales != null && !hasLocale()){
                Locale[] old = Vars.locales;
                // 内置的 router 彩蛋永远排在最后，把新语言塞在它前面
                int insert = old.length;
                for(int i = 0; i < old.length; i++){
                    if(old[i].getLanguage().equals("router")){
                        insert = i;
                        break;
                    }
                }

                Locale[] next = new Locale[old.length + 1];
                System.arraycopy(old, 0, next, 0, insert);
                next[insert] = cns;
                System.arraycopy(old, insert, next, insert + 1, old.length - insert);
                Vars.locales = next;
            }

            if(!Vars.headless){
                LanguageDialog.displayNames.put(langCode, langName);
            }

            Log.info("[ChineseRedstone] 已注册语言: @ (@)", langName, langCode);
        }catch(Throwable t){
            Log.err("[ChineseRedstone] 无法注册语言。", t);
        }
    }

    private boolean hasLocale(){
        for(Locale locale : Vars.locales){
            if(locale != null && langCode.equals(locale.getLanguage())) return true;
        }
        return false;
    }

    private void injectBundle(){
        try{
            if(Core.bundle == null) return;

            // Core.bundle 拿不到 locale（cns 没有对应文件时是 ROOT），只能看设置项
            if(!langCode.equals(Core.settings.getString("locale", "default"))) return;

            try(InputStream stream = openBundle()){
                if(stream == null){
                    Log.warn("[ChineseRedstone] 找不到 @，语言包没有加载。", bundleFile);
                    return;
                }
                try(InputStreamReader reader = new InputStreamReader(stream, StandardCharsets.UTF_8)){
                    PropertiesUtils.load(Core.bundle.getProperties(), reader);
                }
                Log.info("[ChineseRedstone] 已注入 @ 条文本，item.copper = @",
                    Core.bundle.getProperties().size, Core.bundle.get("item.copper.name"));
            }
        }catch(Throwable t){
            Log.err("[ChineseRedstone] 无法注入语言包。", t);
        }
    }

    private InputStream openBundle(){
        // 打包成 jar / 目录安装时都能通过类加载器读到模组根目录的资源
        ClassLoader loader = ChineseRedstoneMod.class.getClassLoader();
        if(loader != null){
            InputStream stream = loader.getResourceAsStream(bundleFile);
            if(stream != null) return stream;
        }

        // 退路：从模组自己的根目录读
        try{
            Mods.LoadedMod mod = Vars.mods == null ? null : Vars.mods.getMod(ChineseRedstoneMod.class);
            if(mod != null && mod.root != null){
                Fi file = mod.root.child(bundleFile);
                if(file.exists()) return file.read();
            }
        }catch(Throwable ignored){
        }
        return null;
    }
}
