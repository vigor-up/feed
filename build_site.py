"""Build the dense, video-led Huolide brand and product site."""

from __future__ import annotations

from datetime import date
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import hashlib
import subprocess

from opencc import OpenCC
import site_data as data

ROOT = Path(__file__).resolve().parent
SITE = "https://richtrong.com"
VIDEO = "https://v.feed-pet.com"
MEDIA = "https://media.feed-pet.com"
TO_SIMPLIFIED = OpenCC("t2s")


def asset_version(name: str) -> str:
    """Content-derived query string so browsers refresh changed shared assets."""
    asset = ROOT / "assets" / name
    return hashlib.sha256(asset.read_bytes()).hexdigest()[:12]

# --- SEO (2026-11-14): stable sitemap lastmod + OG variants -----------------
PAGE_META: dict[str, dict[str, str]] = {}
DESC_BOOST = ("活力得®以重組蛋白酶與活性游離硅為單一複合功能材料，整理母豬、蛋雞、育肥豬、肉雞與魚蝦的"
              "生產指標、比較口徑與技術影音，供獸醫師、飼料配方師與農場經營者評估。")


def og_variant(image: str) -> str:
    stem = Path(image.rsplit("/", 1)[-1]).stem
    f = ROOT / "assets" / "og" / (stem + "-1200x630.webp")
    return SITE + "/assets/og/" + stem + "-1200x630.webp" if f.exists() else image


def body_key(html: str) -> str:
    m = re.search(r'<main id="main">(.*?)</main>', html, re.S)
    return hashlib.sha256((m.group(1) if m else html).encode("utf-8")).hexdigest()[:16]


def git_file_date(rel_path: str) -> str | None:
    if not rel_path:
        return None
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel_path],
                           cwd=ROOT, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() or None
    except Exception:
        return None


def load_sitemap_dates() -> dict:
    try:
        return json.loads((ROOT / "sitemap_dates.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_sitemap_dates(d: dict) -> None:
    (ROOT / "sitemap_dates.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
# ---------------------------------------------------------------------------

# Numbers and wording are transcribed from the current 2026 PPT manifests and
# the published video site's config. A target is labelled as a target.
PRODUCT_STORIES = {
    "junzaiwang": {
        "hook": "繁殖力不只看產仔數，也看母體能否持續承載。",
        "value": "21–22 → >28", "unit": "PSY", "metric": "每頭母豬年斷奶仔豬數",
        "basis": "台灣 6,000 頭母豬場紀錄；依同場繁殖週期與離乳口徑閱讀。",
        "source": "2026 活力得繁殖線簡報 D2・第 7 頁",
        "secondary": [("1.80 → 2.33", "年胎次"), ("<7 → >10 kg", "離乳重")],
        "vet": "看母豬體況、肢蹄與離乳後發情間隔，連接母體承載和下一胎。",
        "formulator": "按妊娠、泌乳與保育階段核對日糧蛋白利用及礦物質供給。",
        "farmer": "用 PSY、同窩均勻度與離乳重，把產房變化換算為每母豬年產出。",
    },
    "keliwang": {
        "hook": "每天一顆蛋的輸出，考驗蛋殼與骨骼的結構。",
        "value": "+12–15%", "unit": "厚度", "metric": "蛋殼厚度的比較值",
        "basis": "蛋雞蛋殼對照；厚度、破損率與產蛋率分開記錄。",
        "source": "2026 活力得家禽線簡報 D5・第 6–7 頁",
        "secondary": [("3% → 1.5%", "破損率"), ("+2.8%", "產蛋率")],
        "vet": "查看產蛋後期骨骼與蛋殼結構，區分營養壓力和管理因素。",
        "formulator": "把蛋白利用、鈣磷與游離硅結構路徑放在同一日糧框架檢視。",
        "farmer": "按商品蛋分級、破損與高峰期日數核算可售蛋量。",
    },
    "duoluanzhuang": {
        "hook": "種苗品質，是養殖利潤的起點。",
        "value": "85%+", "unit": "目標", "metric": "高值海水魚親本受精率管理目標",
        "basis": "受精率 85%+ 為管理目標，並以親本繁殖週期觀察。",
        "source": "2026 活力得繁殖線簡報 D2・第 13 頁",
        "secondary": [("受精率", "親本"), ("孵化率", "種苗")],
        "vet": "把親本體況、卵質、孵化與苗期健康放進同一繁殖週期。",
        "formulator": "依親本魚種與產卵階段核對蛋白供給和結構營養。",
        "farmer": "按每批有效受精卵、可售苗量與苗種單價計算收益。",
    },
    "zhangbiaowang": {
        "hook": "利潤不只在增重，也在飼料利用與胴體結構。",
        "value": "2.0", "unit": "FCR 管理目標", "metric": "育肥豬料肉比目標",
        "basis": "以同一育肥批次的總飼料投入（kg）÷ 活重增量（kg）計算；2.0 為目標值。",
        "source": "內部 FCR_benchmark.jpg 指標稿；田間比較數據見 D3 第 10 頁",
        "secondary": [("−74%", "糞篩未消化殘渣"), ("12.45 → 3.21 g", "糞篩對照")],
        "vet": "從糞篩、體況和肢蹄觀察營養利用與結構壓力。",
        "formulator": "同批比較日糧蛋白、採食量與可消化養分損失。",
        "farmer": "以活重增量、飼料投入、背膘與胴體計價核算每頭利潤。",
    },
    "zujinwang": {
        "hook": "同樣吃料，胸肉與出欄規格能多多少？",
        "value": "+15.24%", "unit": "胸肉", "metric": "肉雞胸肉產量比較",
        "basis": "肉雞企業實證；收益需依同一屠宰規格與當地成雞價格閱讀。",
        "source": "2026 活力得家禽線簡報 D5・第 10 頁",
        "secondary": [("−2.5–3.2%", "FCR"), ("+3.4–3.9%", "出欄重")],
        "vet": "觀察腿部承載、體況與生長速度的平衡。",
        "formulator": "按白羽與黃羽品系分開核算蛋白利用、FCR 和日糧成本。",
        "farmer": "把胸肉、可售胴體、出欄重與每批飼料投入放進 ROI。",
    },
    "baomiaowang": {
        "hook": "苗期育成率，決定一整池的收成起點。",
        "value": "60% → 80%", "unit": "育成", "metric": "場域幼蝦育成率對照",
        "basis": "台灣場域幼蝦紀錄；魚類增重與蝦類育成分開閱讀。",
        "source": "2026 活力得水產線簡報 D6・第 13 頁",
        "secondary": [("18% → 12%", "規格 CV"), ("+44.6%", "午仔魚存活")],
        "vet": "把腸道、脫殼、病原壓力和水質放在同一池次檢視。",
        "formulator": "按蝦種、魚種與苗期密度核對蛋白利用和投餌策略。",
        "farmer": "以放苗量、可售尾數、規格與投餌成本計算每池收益。",
    },
}


def poster_style(object_name: str, brand: bool = False, brand_image: str = "brand") -> str:
    if brand:
        image = "/assets/species/cattle.webp" if brand_image == "cattle" else "/assets/scenes/brand.webp"
        return f"background-image:url('{image}');background-size:cover;background-position:center"
    object_name = SCI_REV.get(object_name, object_name)   # 新媒體檔名 → 原代號(卡片圖/場景圖以原代號命名)
    if object_name in {s[0] for s in SCI_NEW}:   # 新科普片:輪播底圖用各自的 GPT Image 卡片圖
        return f"background-image:url('/assets/cards/{object_name}.webp');background-size:cover;background-position:center"
    if object_name.startswith("sci-"):
        if object_name == "sci-v02":
            return "background-image:url('/assets/scenes/science-hero.png');background-size:cover;background-position:center"
        index = 0 if object_name == "sci-v02" else 1
        return f"background-image:url('/assets/scenes/science.webp');background-size:200% auto;background-position:{index * 100}% 0%"
    match = re.match(r"p([1-6])-v(\d+)", object_name)
    if not match:
        raise ValueError(f"No generated poster mapping for {object_name}")
    product, number = int(match.group(1)), int(match.group(2))
    order = [video[1] for video in data.PRODUCTS[product - 1][5]]
    index = order.index(object_name)
    if index == 0:
        return f"background-image:url('/assets/scenes/p{product}-hero.png');background-size:cover;background-position:center"
    rows = 3 if product in (2, 3) else 2
    x = 100 if index % 2 else 0
    y = (index // 2) * (100 if rows == 2 else 50)
    size = "auto 300%" if rows == 3 else "200% auto"
    return f"background-image:url('/assets/scenes/p{product}.webp');background-size:{size};background-position:{x}% {y}%"


class VisibleImages(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "img" and a.get("src"):
            self.paths.append(a["src"])
        if tag == "video" and a.get("poster"):
            self.paths.append(a["poster"])
        if a.get("style"):
            self.paths.extend(re.findall(r"background-image:url\('([^']+)'\)", a["style"]))


def verify_unique_visible_images(routes: list[str]) -> None:
    for route in routes:
        path = ROOT / route / "index.html" if route.endswith("/") or not route else ROOT / route
        parser = VisibleImages()
        parser.feed(path.read_text(encoding="utf-8"))
        counts = Counter(x for x in parser.paths if "logo" not in x and "36751031" not in x)
        duplicate = {image: n for image, n in counts.items() if n > 1}
        if duplicate:
            raise ValueError(f"Repeated visible image on {route or '/'}: {duplicate}")
    print(f"DEDUP PASS pages={len(routes)} duplicate_visible_images=0")


def hero_video(object_name: str, label: str, watch: str, brand: bool = False, brand_image: str = "brand") -> str:
    preview = f"{MEDIA}/{object_name}-hero-h.mp4"
    if brand:
        preview = f"{MEDIA}/brand-v05-v5-hero-h.mp4"
    return f'''<div class="film-stage"><video class="motion-preview hero-film" muted loop playsinline preload="none" style="{poster_style(object_name, brand, brand_image)}" data-preview="{preview}" aria-label="{escape(label, quote=True)}"></video><div class="film-bar"><span>活力得® · 影音紀錄</span><a href="{watch}">觀看完整影片 <span aria-hidden="true">↗</span></a></div></div>'''


# 2026-11-18 第二批技術科普片(總監 gate pass;影音館各有獨立觀看頁 /s/<slug>/,VideoObject 只在影音館宣告)
SCI_NEW = [
    ("sci-v04", "攪拌越快，酶越快死？流場結構決定穩定性", "製程研發・技術壁壘", ["剪切讓酶解摺疊失活", "泰勒渦流：沒有攪拌棒的共組裝"]),
    ("sci-v05", "量產為什麼翻車？放大不是把設備做大", "製程研發・技術壁壘", ["放大不是把設備做大", "溫度・流量・停留時間 三參數鎖住"]),
    ("sci-v06", "同款設備，為何結果不同？", "製程研發・技術壁壘", ["設備買得到，參數窗口買不到", "4–10°C × 30–120 秒"]),
    ("sci-v07", "1 公斤憑什麼贏 25 公斤？", "科普・生物機轉", ["蛋白酶像剪刀，可重複使用", "育肥豬 FCR 2.8 → 2.0"]),
    ("sci-v08-r2", "細菌也當工人？枯草桿菌的蛋白酶", "科普・生物機轉", ["土壤篩選的枯草桿菌", "把蛋白酶分泌到細胞外"]),
    ("sci-v09", "奈米硅其實只是奈米石頭", "製程研發・技術壁壘", ["磨得再細也是石頭：吸收率 < 0.2%", "泰勒渦流＋玻璃態鎖存，扛過 85°C 製粒"]),
    ("sci-v10", "低蛋白日粮，真正要解决的是什么？", "配方决策", ["两成以上蛋白没被消化就排掉", "下修粗蛋白＋补足氨基酸＋加蛋白酶"]),
]
SCI_WATCH = {"sci-v01", "sci-v02", "sci-v03-r2", "sci-mech-r2"} | {s[0] for s in SCI_NEW}
# 2026-11-18 讀音修正後科普片換新音軌:R2 媒體檔不可覆寫,改用新檔名;影音館觀看頁同名(舊網址 301)。
# 卡片圖仍以原代號命名,這裡只換媒體/觀看頁名稱。
SCI_MEDIA = {"sci-v10": "sci-v10-r2", "sci-v09": "sci-v09", "sci-v01": "sci-v01-r3", "sci-v02": "sci-v02-r3", "sci-v03-r2": "sci-v03-r4", "sci-mech-r2": "sci-mech-r3",
             "sci-v04": "sci-v04-r3", "sci-v05": "sci-v05-r3", "sci-v06": "sci-v06-r3", "sci-v07": "sci-v07-r3", "sci-v08-r2": "sci-v08-r4"}
SCI_REV = {v: k for k, v in SCI_MEDIA.items()}
BRAND_OBJ = "brand-v05-v6-h"   # 品牌片 v4(讀音修正後新版次)


def video_card(video_slug: str, object_name: str, title: str) -> str:
    watch = (f"{VIDEO}/s/{SCI_MEDIA.get(video_slug, video_slug)}/" if video_slug in SCI_WATCH else f"{VIDEO}/tech/") if video_slug.startswith("sci-") else f"{VIDEO}/v/{video_slug}/"
    poster = f"/assets/cards/{video_slug}.webp"
    if not (ROOT / poster.lstrip("/")).is_file():
        raise FileNotFoundError(f"Missing GPT Image card art: {poster}")
    return f'''<article class="video-card"><a class="video-thumb" href="{watch}" aria-label="觀看影片：{escape(title, quote=True)}"><img src="{poster}" alt="{escape(title, quote=True)}" loading="lazy" decoding="async"><span class="play">▶</span></a><div class="video-meta"><h3>{escape(title)}</h3><a href="{watch}">影片重點 ↗</a></div></article>'''


def hero_carousel() -> str:
    mechanism_clips = {
        "p1-v01", "p1-v03", "p1-v04", "p2-v01", "p2-v02", "p2-v04",
        "p3-v01", "p3-v03", "p3-v04", "p3-v05", "p4-v02", "p4-v03",
        "p5-v04", "p6-v01", "p6-v03",
    }
    clips = [
        *[{"id":s, "object":SCI_MEDIA[s], "title":t, "category":c, "priority":True, "points":pts, "src":f"{MEDIA}/{SCI_MEDIA[s]}.mp4",
           "watch":f"{VIDEO}/s/{SCI_MEDIA[s]}/"} for s, t, c, pts in [
            ("sci-v02", "每一批，都從製程穩定開始", "製程研發・技術壁壘", ["批次穩定，從製程控制開始", "重組蛋白酶 × 活性游離硅"]),
            ("sci-v03-r2", "游離硅，從原料到結構營養", "科普・材料技術", ["游離硅，連接結構營養", "骨・蹄・殼，回到生產指標"]),
            ("sci-v01", "看懂重組蛋白酶的作用路徑", "科普・生物機轉", ["重組蛋白酶，聚焦蛋白質利用", "從作用路徑，看到日糧效率"]),
            ("sci-mech-r2", "從分子作用到飼料利用", "科普・生物機轉", ["從分子作用，回到飼料利用", "蛋白利用 × 結構營養"])] + SCI_NEW],
        {"id":"brand-v05","object":BRAND_OBJ,"title":"同樣的料，為什麼隔壁欄賺更多？","category":"品牌精神","priority":True,"points":["別只看投入；更要看可售產出","6 條產品線，對應現場痛點"],"src":f"{MEDIA}/brand-v05-v5-h.mp4","watch":f"{VIDEO}/v/brand-v05/"},
    ]
    for product_index, product in enumerate(data.PRODUCTS, 1):
        slug, name, audience, _, _, videos = product
        story = PRODUCT_STORIES[slug]
        for video_slug, object_name, title in videos:
            priority = video_slug in mechanism_clips
            clips.append({
                "id":video_slug, "object":object_name, "title":title,
                "category":"科普・生物機轉" if priority else f"{audience}・生產痛點",
                "priority":priority,
                "points":[f"{story['value']} {story['unit']}｜{story['metric']}", f"聚焦 {title.rstrip('？?。')}｜回到每批可售產出"],
                "src":f"{MEDIA}/{object_name}-h.mp4",   # 20261118 修直橫:16:9 輪播用橫式檔(無尾碼的是 9:16 直式)
                "watch":f"{VIDEO}/v/{video_slug}/", "product":name,
                "poster":poster_style(object_name),
            })
    for clip in clips:
        clip.setdefault("poster", poster_style(clip["object"], clip["id"].startswith("brand-")))
    preferred = sum(1 for clip in clips if clip["priority"])
    if len(clips) != 32 + len(SCI_NEW) or preferred <= len(clips) / 2:
        raise ValueError(f"Hero carousel gate failed: {preferred}/{len(clips)} priority videos")
    playlist = escape(json.dumps(clips, ensure_ascii=False, separators=(",", ":")), quote=False)
    first = next(clip for clip in clips if clip["priority"])
    return f'''<section class="hero hero-cinema" id="top" data-priority-count="{preferred}" data-total-count="{len(clips)}"><div class="hero-fallback" style="{poster_style(first['object'], first['id'].startswith('brand-'))}" aria-hidden="true"></div><video class="hero-reel" autoplay muted playsinline preload="metadata" aria-label="活力得®產品與技術影片輪播"></video><div class="hero-copy wrap"><p class="kicker">活力得® / 飼料添加劑・單一複合材料</p><h1>同一批料，<br><em>利潤差在哪？</em></h1><p class="hero-current"><span id="hero-category">{escape(first['category'])}</span><strong id="hero-title">{escape(first['title'])}</strong></p><ul class="hero-points" id="hero-points" aria-label="影片重點"><li>{escape(first['points'][0])}</li><li>{escape(first['points'][1])}</li></ul><div class="hero-metrics"><b>21–22 → &gt;28 <small>PSY</small></b><b>2.0 <small>FCR目標</small></b><b>+15.24% <small>胸肉</small></b><b>60% → 80% <small>育成率</small></b></div><div class="hero-actions"><a class="button solid" id="hero-watch" href="{first['watch']}">觀看完整影片 ↗</a><button class="button outline" id="hero-sound" type="button" aria-pressed="false">播放旁白</button></div><div class="hero-controls"><button type="button" id="hero-prev" aria-label="上一支影片">←</button><span id="hero-index" aria-live="polite">01 / {len(clips)}</span><button type="button" id="hero-next" aria-label="下一支影片">→</button><button type="button" id="hero-motion" aria-label="暫停影片輪播">暫停</button><span class="hero-audience">獸醫師 / 飼料配方師 / 農場經營者</span></div></div><div class="film-bar"><span>活力得® · 影音精選</span><a href="{VIDEO}/">全部影音 ↗</a></div><script type="application/json" id="hero-playlist">{playlist}</script></section>'''


def value_story() -> str:
    return '''<section class="value-section" id="value"><div class="wrap"><div class="value-intro"><p class="kicker">經營價值 / ROI</p><h2>看可售量、料效與規格，<br>就看見利潤空間。</h2><p>從同批次的產出與飼料投入，找出每個生產階段最值得改善的數字。</p></div><div class="value-grid"><a href="/products/keliwang.html"><span>商品蛋 / 可售量</span><strong>3% → 1.5%</strong><p>破損率變化，直接影響可售蛋數。</p></a><a href="/products/zujinwang.html"><span>肉雞 / 可售部位</span><strong>+15.24%</strong><p>胸肉產量比較，連接出欄規格與部位價值。</p></a><a href="/products/baomiaowang.html"><span>水產 / 苗期育成</span><strong>60% → 80%</strong><p>育成率變化，連接放苗量與可售尾數。</p></a></div></div></section>'''


def page(path: str, title: str, description: str, body: str, image: str | None = None) -> None:
    rel = path.removesuffix("index.html")
    canonical = SITE + "/" + rel
    simplified_url = SITE + "/zh-cn/" + rel
    image = image or SITE + "/assets/species/sow.webp"
    og_image = og_variant(image)
    if len(description) < 70:
        description = description.rstrip("。") + "。" + DESC_BOOST
    nav = '<a href="/">首頁</a><a href="/technology.html">核心技術</a><a href="/products/">產品線</a><a href="/stories.html">影音故事</a>'
    crumbs = [{"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE + "/"}]
    if rel:
        crumbs.append({"@type": "ListItem", "position": 2, "name": title.split("｜")[0], "item": canonical})
    schema = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": title, "url": canonical, "description": description,
         "isPartOf": {"@type": "WebSite", "name": "活力得®", "url": SITE + "/"}},
        {"@type": "Organization", "name": "活力得®", "url": SITE + "/",
         "logo": {"@type": "ImageObject", "url": SITE + "/assets/huolide-36751031.png"},
         "sameAs": [VIDEO + "/"]},
        {"@type": "WebSite", "name": "活力得®", "url": SITE + "/", "inLanguage": ["zh-Hant", "zh-Hans"]},
        {"@type": "BreadcrumbList", "itemListElement": crumbs}]}, ensure_ascii=False)
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="same-origin"><title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="zh-Hant" href="{canonical}"><link rel="alternate" hreflang="zh-Hans" href="{simplified_url}"><link rel="alternate" hreflang="x-default" href="{canonical}"><meta property="og:type" content="website"><meta property="og:locale" content="zh_TW"><meta property="og:site_name" content="活力得®"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{og_image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="活力得®動物營養材料"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/png" href="/assets/huolide-36751031.png"><link rel="apple-touch-icon" href="/assets/huolide-36751031.png"><link rel="stylesheet" href="/assets/site.css?v={asset_version('site.css')}"><script src="/assets/site.js?v={asset_version('site.js')}" defer></script><script type="application/ld+json">{schema}</script></head><body><a class="skip" href="#main">跳至內容</a><header class="site-header"><a class="brand" href="/" aria-label="活力得®首頁"><img src="/assets/huolide-36751031.png" alt="活力得®註冊圖形商標"><span>活力得<sup>®</sup><small>HUOLIDE · ANIMAL NUTRITION</small></span></a><nav aria-label="主要導覽">{nav}</nav><a class="header-action" href="/#value">經營價值 ↗</a></header><main id="main">{body}</main><footer><div class="footer-top"><div class="footer-brand"><img src="/assets/huolide-36751031.png" alt="活力得®圖形商標"><div><strong>活力得<sup>®</sup></strong><p>重組蛋白酶與活性游離硅的單一複合功能材料</p></div></div><div class="footer-links"><a href="/technology.html">材料技術</a><a href="/products/">六條產品線</a><a href="/stories.html">影音故事</a><a href="{VIDEO}/">完整影音館</a><a href="{simplified_url}" lang="zh-Hans">简体中文</a></div></div><div class="footer-bottom"><span>活力得® 註冊商標 · 第 36751031 號</span><span>獸醫師 · 飼料配方師 · 農場經營者</span></div></footer></body></html>'''
    out = ROOT / (path or "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    PAGE_META[rel] = {"key": body_key(html), "path": str(out.relative_to(ROOT))}
    simplified = TO_SIMPLIFIED.convert(html)
    simplified = simplified.replace('lang="zh-Hant"', 'lang="zh-Hans"', 1)
    simplified = simplified.replace(f'<link rel="canonical" href="{canonical}">', f'<link rel="canonical" href="{simplified_url}">', 1)
    simplified = simplified.replace(f'<meta property="og:url" content="{canonical}">', f'<meta property="og:url" content="{simplified_url}">', 1)
    simplified = simplified.replace('content="zh_TW"', 'content="zh_CN"', 1)
    simplified = simplified.replace(f'"url": "{canonical}"', f'"url": "{simplified_url}"', 1)
    simplified = simplified.replace(f'"item": "{canonical}"', f'"item": "{simplified_url}"', 1)
    simplified = simplified.replace(f'<a href="{simplified_url}" lang="zh-Hans">简体中文</a>', f'<a href="{canonical}" lang="zh-Hant">繁體中文</a>')
    simplified = re.sub(r'href="/(?!assets/|zh-cn/)', 'href="/zh-cn/', simplified)
    simplified_out = ROOT / "zh-cn" / (path or "index.html")
    simplified_out.parent.mkdir(parents=True, exist_ok=True)
    simplified_out.write_text(simplified, encoding="utf-8")


def product_card(product: tuple) -> str:
    slug, name, audience, _, _, videos = product
    story = PRODUCT_STORIES[slug]
    first = videos[0][1]
    return f'''<a class="product-card" href="/products/{slug}.html"><div class="product-film"><video class="motion-preview" muted loop playsinline preload="none" style="{poster_style(first)}" data-preview="{MEDIA}/{first}-hero-h.mp4" aria-hidden="true"></video><span class="product-index">{escape(audience)}</span></div><div class="product-card-copy"><div><h3>{escape(name)}</h3><p>{escape(story['hook'])}</p></div><div class="product-stat"><strong>{escape(story['value'])}</strong><span>{escape(story['metric'])}</span></div><span class="product-arrow">探索產品與影片 ↗</span></div></a>'''


def market_taxonomy() -> str:
    groups = [
        ("pig", "豬", [("仔豬／保育豬", "/products/junzaiwang.html"), ("哺乳母豬", "/products/junzaiwang.html"), ("育肥豬", "/products/zhangbiaowang.html"), ("種公豬", None)]),
        ("ruminant", "牛羊", [("奶牛", "/products/ruminants.html"), ("肉牛", "/products/ruminants.html"), ("綿羊／肉羊", "/products/ruminants.html"), ("奶山羊", "/products/ruminants.html")]),
        ("poultry", "家禽", [("白羽肉雞", "/products/zujinwang.html"), ("黃羽肉雞", "/products/zujinwang.html"), ("蛋雞", "/products/keliwang.html"), ("三黃雞", None), ("土雞", None), ("種雞", None), ("鴨", None), ("鵝", None)]),
        ("aquaculture", "水產", [("養殖淡水魚", "/products/baomiaowang.html"), ("養殖海水魚", "/products/baomiaowang.html"), ("養殖蝦", "/products/baomiaowang.html"), ("養殖蟹", None), ("養殖貝類", None)]),
    ]
    cards = []
    for ident, heading, items in groups:
        chips = "".join(f'<a href="{link}">{escape(label)} ↗</a>' if link else f'<span>{escape(label)}</span>' for label, link in items)
        cards.append(f'<article id="{ident}"><h3>{heading}</h3><div class="market-chips">{chips}</div></article>')
    return '<section class="market-taxonomy wrap"><div class="section-head"><p class="kicker">中國市場 / 物種與生產階段</p><h2>先找到物種，<br>再讀對應數據。</h2></div><div class="market-groups">' + "".join(cards) + '</div></section>'


def species_gallery() -> str:
    animals = [
        ("sow", "繁殖母豬", "從 PSY 到離乳重", "junzaiwang"),
        ("cattle", "肉牛與反芻", "按物種與日糧階段設計", "ruminants"),
        ("broiler", "白羽肉雞", "看胸肉、出欄與料效", "zujinwang"),
        ("shrimp", "養殖蝦", "從苗期育成率看收益", "baomiaowang"),
    ]
    cards = "".join(
        f'<a class="species-card" href="/products/{slug}.html"><img src="/assets/species/{ident}.webp" alt="{name}養殖場景" loading="lazy" width="1536" height="1024"><span><strong>{name}</strong><small>{subtitle} ↗</small></span></a>'
        for ident, name, subtitle, slug in animals
    )
    return '<section class="species-section wrap"><div class="section-head inline"><div><p class="kicker">市場場景 / 物種焦點</p><h2>從現場出發，<br>回到每一批的生產帳。</h2></div><a class="text-link" href="/products/">探索完整物種分類 ↗</a></div><div class="species-grid">' + cards + '</div></section>'


def slug_to_number(slug: str) -> int:
    return [p[0] for p in data.PRODUCTS].index(slug) + 1


def build() -> None:
    product_cards = "".join(product_card(product) for product in data.PRODUCTS)
    stats = "".join(
        f'<a href="/products/{slug}.html"><span>{escape(PRODUCT_STORIES[slug]["metric"])}</span><strong>{escape(PRODUCT_STORIES[slug]["value"])}</strong></a>'
        for slug in ("junzaiwang", "zhangbiaowang", "zujinwang", "baomiaowang")
    )
    home = f'''{hero_carousel()}<section class="section-products wrap"><div class="section-head inline"><div><p class="kicker">六條產品線 / 對應六類現場問題</p><h2>看痛點，<br>找能改變的指標。</h2></div><a class="text-link" href="/products/">依物種瀏覽 ↗</a></div><div class="product-grid">{product_cards}</div></section>{species_gallery()}<section class="tech-feature"><div class="wrap"><div><p class="kicker">材料技術</p><h2>蛋白質利用 ×<br>結構營養。</h2><p>重組蛋白酶與活性游離硅，連接飼料利用與骨、蹄、殼的結構支持。</p><a class="button outline" href="/technology.html">看技術與製程 ↗</a></div>{hero_video('sci-v03-r2', '游離硅與結構營養', VIDEO+'/tech/')}</div></section>{value_story()}'''
    page("", "活力得®｜重組蛋白酶與游離硅飼料添加劑・產品數據與 ROI", "活力得®動物營養材料：從生產指標、六條產品線與影片，了解母豬、蛋雞、育肥豬、肉雞、魚蝦的生產指標與經營價值。", home)

    tech = f'''<section class="inner-hero cinematic"><div><p class="kicker">材料技術 / 製程 / 品質</p><h1>蛋白質利用，<br><em>連接結構營養。</em></h1><p>活力得®以重組 C 系絲氨酸蛋白酶與游離硅相關組分，構成單一複合功能材料。獸醫師看組織，配方師看日糧，農場主看可售產出與投入。</p></div>{hero_video('sci-v02', '連續流反應器與製程', VIDEO+'/tech/')}</section><section class="tech-panes wrap"><article><span>PROTEASE / 蛋白質利用</span><h2>重組蛋白酶</h2><p>絲氨酸蛋白酶以 Ser–His–Asp 催化三聯體參與蛋白水解，對應小肽與胺基酸供給。</p></article><article><span>SILICON / 結構營養</span><h2>活性游離硅</h2><p>游離硅相關組分連接膠原基質、骨礦化與殼部結構，與蛋白利用放在同一材料軸心。</p></article></section><section class="section-videos wrap"><div class="section-head inline"><div><p class="kicker">技術影音</p><h2>把製程和作用路徑看清楚。</h2></div></div><div class="video-grid">{video_card('sci-v02','sci-v02','同一台反應器，為什麼每一批都一樣？')}{video_card('sci-v03-r2','sci-v03-r2','硅不是加了就有用')}{''.join(video_card(s, s, t) for s, t, _, _ in SCI_NEW)}</div></section>'''
    page("technology.html", "活力得®核心技術｜重組蛋白酶與游離硅複合材料", "閱讀活力得®重組 C 系絲氨酸蛋白酶、游離硅材料與連續流製程，並觀看已發布技術影片。", tech)

    listing = f'''<section class="inner-title wrap"><p class="kicker">中國市場 / 依物種與階段</p><h1>六條產品，<em>對應不同生產帳。</em></h1><p>先找物種，再看 PSY、FCR、蛋殼、胸肉、育成率與可售苗量；每條產品都回到自身的批次與收益口徑。</p></section><section class="section-products wrap tight"><div class="product-grid">{product_cards}</div></section>{market_taxonomy()}{value_story()}'''
    page("products/index.html", "活力得®六條飼料添加劑產品線｜豬禽牛羊魚蝦", "依物種與生產階段瀏覽活力得®六條產品線、產品數據、影片與經營價值。", listing)

    ruminants = f'''<section class="inner-hero cinematic"><div><p class="kicker">反芻動物 / 生產型態</p><h1>牛羊營養，<br><em>從採食到出欄。</em></h1><p>肉牛肉羊的育肥、奶牛奶羊的泌乳，各有不同的日糧、體況與收益口徑。重組蛋白酶與游離硅的複合材料軸心，連接蛋白利用與蹄部、骨架結構。</p><a class="button solid" href="/products/">看物種與產品 ↗</a></div>{hero_video('brand-v05-v5-h','牛羊品牌故事',VIDEO+'/v/brand-v05/',True,'cattle')}</section><section class="tech-panes wrap"><article><span>MEAT / 肉用</span><h2>肉牛・肉羊</h2><p>按同物種和育肥階段追蹤採食、日增重、終重、FCR、肢蹄與出欄價格。</p></article><article><span>DAIRY / 乳用</span><h2>奶牛・奶山羊</h2><p>將泌乳量、乳成分、體況、採食與肢蹄紀錄分開閱讀，不套用肉用動物的數值。</p></article></section>'''
    page("products/ruminants.html", "牛羊飼料利用與結構營養｜活力得®", "依肉牛、肉羊、奶牛和奶山羊生產型態閱讀飼料利用、採食、泌乳或出欄指標與本場 ROI。", ruminants)

    for slug, name, audience, _, _, videos in data.PRODUCTS:
        story = PRODUCT_STORIES[slug]
        first = videos[0][1]
        side_stats = "".join(f'<div><strong>{escape(number)}</strong><span>{escape(label)}</span></div>' for number, label in story['secondary'])
        focus = "".join(f'<article><strong>{escape(label)}</strong><p>{escape(detail)}</p></article>' for label, detail in data.FIELD_FOCUS[slug])
        cards = "".join(video_card(*video) for video in videos)
        body = f'''<section class="inner-hero product-hero cinematic"><div><p class="kicker">{escape(audience)} / 活力得®產品線</p><h1>{escape(name)}<em>{escape(story['hook'])}</em></h1><p>看同一批的採食、增重、可售規格與投入；從獸醫評估到配方調整，找到真正留下利潤的環節。</p><div class="hero-actions"><a class="button solid" href="#numbers">看核心數據 ↘</a><a class="button outline" href="#field">看生產指標 ↘</a></div></div>{hero_video(first,name+'產品影片',VIDEO+'/v/'+videos[0][0]+'/')}</section><section class="number-story wrap" id="numbers"><div class="number-big"><p class="kicker">場域數字 / {escape(name)}</p><strong>{escape(story['value'])}</strong><span>{escape(story['unit'])} · {escape(story['metric'])}</span><p>{escape(story['basis'])}</p></div><div class="number-side"><h2>數字背後，<br>是可重算的生產帳。</h2>{side_stats}</div></section><section class="audience-section wrap"><div class="section-head"><p class="kicker">從三個專業視角閱讀</p><h2>同一批數據，<br>對應三種決策。</h2></div><div class="audience-grid"><article><span>VET / 獸醫師</span><p>{escape(story['vet'])}</p></article><article><span>FORMULATION / 配方師</span><p>{escape(story['formulator'])}</p></article><article><span>FARM / 農場主</span><p>{escape(story['farmer'])}</p></article></div></section><section class="field-section wrap" id="field"><div><p class="kicker">田間紀錄 / 比較口徑</p><h2>把優勢寫進<br>同批次紀錄。</h2></div><div class="field-grid">{focus}</div></section><section class="section-videos wrap"><div class="section-head inline"><div><p class="kicker">{escape(name)} / 已發布影音</p><h2>看現場問題，<br>再看材料解法。</h2></div><a class="text-link" href="{VIDEO}/p/{slug}/">完整產品影音頁 ↗</a></div><div class="video-grid">{cards}</div></section>'''
        page(f"products/{slug}.html", f"{name}｜{audience}生產數據與 ROI｜活力得®", f"{name}對應{audience}。閱讀{story['metric']}、場域比較口徑、獸醫與配方視角，觀看已發布影片與經營價值。", body, f"{SITE}/assets/scenes/p{slug_to_number(slug)}.webp")

    featured = [data.PRODUCTS[0][5][0], data.PRODUCTS[1][5][0], data.PRODUCTS[3][5][1], data.PRODUCTS[4][5][2], data.PRODUCTS[5][5][0]]
    stories = f'''<section class="inner-title wrap"><p class="kicker">活力得® / 影音故事</p><h1>每個數字背後，<em>都有一個現場問題。</em></h1><p>從產房、蛋雞舍、育肥場到養殖池，影片以生產問題連接技術與產品。完整版與分段重點都在影音館。</p><a class="button solid" href="{VIDEO}/">進入影音館 ↗</a></section><section class="section-videos wrap"><div class="video-grid">{''.join(video_card(*video) for video in featured)}</div></section>'''
    page("stories.html", "活力得®影音故事｜豬禽水產產品影片", "觀看活力得®豬禽水產產品影片、現場問題與技術故事。", stories)

    for old, destination in data.OLD_ROUTES.items():
        target = f"{SITE}/{destination}"
        dest = ROOT / old
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{target}"><title>頁面已移至活力得®新站</title></head><body><a href="{target}">前往新版頁面</a></body></html>', encoding="utf-8")
    routes = ["", "technology.html", "products/", "stories.html", "products/ruminants.html"] + [f"products/{p[0]}.html" for p in data.PRODUCTS]
    all_routes = routes + [f"zh-cn/{route}" for route in routes]
    today = date.today().isoformat()
    dates = load_sitemap_dates()
    for route in routes:
        meta = PAGE_META.get(route.removesuffix("index.html"), {})
        key = meta.get("key", "")
        cur = dates.get(route, {})
        if not cur:
            cur = {"date": git_file_date(meta.get("path", "")) or today, "key": key}
        elif cur.get("key") and key and cur["key"] != key:
            cur = {"date": today, "key": key}
        else:
            cur["key"] = key
        dates[route] = cur
    save_sitemap_dates(dates)

    def lastmod(route: str) -> str:
        base = route[len("zh-cn/"):] if route.startswith("zh-cn/") else route
        return dates.get(base, {}).get("date", today)

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}/{route}</loc><lastmod>{lastmod(route)}</lastmod></url>\n" for route in all_routes) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    media_sources = {"source_site": VIDEO + "/", "public_r2_base": MEDIA + "/",
                     "brand": {"watch_page": VIDEO + "/v/brand-v05/", "video": MEDIA + "/brand-v05-v5-h.mp4", "preview": MEDIA + "/brand-v05-v5-hero-h.mp4"},
                     "products": [{"slug": slug, "name": name, "source_page": f"{VIDEO}/p/{slug}/",
                                   "videos": [{"watch_page": f"{VIDEO}/v/{video_slug}/", "r2_video": f"{MEDIA}/{object_name}.mp4", "preview": f"{MEDIA}/{object_name}-hero-h.mp4", "poster": f"{VIDEO}/assets/t/{object_name}.jpg", "topic": title}
                                              for video_slug, object_name, title in videos]}
                                  for slug, name, _, _, _, videos in data.PRODUCTS]}
    home_html = (ROOT / "index.html").read_text(encoding="utf-8")
    playlist_match = re.search(r'<script type="application/json" id="hero-playlist">(.*?)</script>', home_html, re.S)
    if not playlist_match:
        raise ValueError("Homepage hero playlist missing")
    media_sources["hero_carousel"] = json.loads(playlist_match.group(1))
    (ROOT / "media-sources.json").write_text(json.dumps(media_sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verify_unique_visible_images(all_routes)
    print(f"BUILD OK pages={len(all_routes)} legacy_redirects={len(data.OLD_ROUTES)} sitemap_urls={len(all_routes)} logo=huolide-36751031.png")


if __name__ == "__main__":
    build()
