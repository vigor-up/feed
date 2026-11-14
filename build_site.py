"""Build the dense, video-led Huolide brand and product site."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
import json
import re

from opencc import OpenCC
import site_data as data

ROOT = Path(__file__).resolve().parent
SITE = "https://richtrong.com"
VIDEO = "https://v.feed-pet.com"
MEDIA = "https://media.feed-pet.com"
TO_SIMPLIFIED = OpenCC("t2s")

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
        "value": "+12–15%", "unit": "厚度", "metric": "蛋殼厚度的簡報比較值",
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
        "basis": "簡報將受精率 85%+ 列為管理目標，並以親本繁殖週期觀察。",
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
        "value": "+15.24%", "unit": "胸肉", "metric": "企業資料中的胸肉產量比較",
        "basis": "肉雞企業實證；收益需依同一屠宰規格與當地成雞價格換算。",
        "source": "2026 活力得家禽線簡報 D5・第 10 頁",
        "secondary": [("−2.5–3.2%", "FCR"), ("+3.4–3.9%", "出欄重")],
        "vet": "觀察腿部承載、體況與生長速度的平衡。",
        "formulator": "按白羽與黃羽品系分開核算蛋白利用、FCR 和日糧成本。",
        "farmer": "把胸肉、可售胴體、出欄重與每批飼料投入放進 ROI。",
    },
    "baomiaowang": {
        "hook": "苗期育成率，決定一整池的收成起點。",
        "value": "60% → 80%", "unit": "育成", "metric": "簡報中的幼蝦育成率對照",
        "basis": "台灣場域幼蝦紀錄；魚類增重與蝦類育成分開閱讀。",
        "source": "2026 活力得水產線簡報 D6・第 13 頁",
        "secondary": [("18% → 12%", "規格 CV"), ("+44.6%", "午仔魚存活")],
        "vet": "把腸道、脫殼、病原壓力和水質放在同一池次檢視。",
        "formulator": "按蝦種、魚種與苗期密度核對蛋白利用和投餌策略。",
        "farmer": "以放苗量、可售尾數、規格與投餌成本計算每池收益。",
    },
}


def hero_video(object_name: str, label: str, watch: str, brand: bool = False) -> str:
    preview = f"{MEDIA}/{object_name}-hero-h.mp4"
    poster = f"{VIDEO}/assets/t/{object_name}.jpg"
    if brand:
        preview = f"{MEDIA}/brand-v05-v3-hero-h.mp4"
        poster = f"{VIDEO}/assets/p/brand-v05-v3-h.jpg"
    return f'''<div class="film-stage"><video class="motion-preview hero-film" muted loop playsinline preload="none" poster="{poster}" data-preview="{preview}" aria-label="{escape(label, quote=True)}"></video><div class="film-bar"><span>活力得® · 影音紀錄</span><a href="{watch}">觀看完整影片 <span aria-hidden="true">↗</span></a></div></div>'''


def video_card(video_slug: str, object_name: str, title: str) -> str:
    poster = f"{VIDEO}/assets/t/{object_name}.jpg"
    preview = f"{MEDIA}/{object_name}-hero-h.mp4"
    return f'''<article class="video-card"><a class="video-thumb" href="{VIDEO}/v/{video_slug}/" aria-label="觀看影片：{escape(title, quote=True)}"><video class="motion-preview" muted loop playsinline preload="none" poster="{poster}" data-preview="{preview}" aria-hidden="true"></video><span class="play">▶</span></a><div class="video-meta"><h3>{escape(title)}</h3><a href="{VIDEO}/v/{video_slug}/">影片與旁白 ↗</a></div></article>'''


def roi_calculator() -> str:
    return '''<section class="roi-section" id="roi"><div class="roi-intro"><p class="kicker">經營決策 / ROI</p><h2>讓場內數字，<br>回答值不值得投入。</h2><p>同場同週期記錄可售產出與飼料投入，再用本場價格換算。售價口徑可選活重、胴體、商品蛋或苗種；計算只在目前瀏覽器進行。</p><div class="roi-equation"><strong>ROI</strong><span>（新增銷售額 ＋ 節料收益 − 方案投入）÷ 方案投入 × 100%</span></div></div><form class="roi-calc" novalidate><div class="roi-form-head"><strong>本場 ROI 試算</strong><small>人民幣 · 本批次</small></div><div class="roi-fields"><label>售價口徑<select name="basis"><option>活重</option><option>胴體</option><option>商品蛋</option><option>苗種</option></select></label><label>新增可售量<input name="extra" type="number" min="0" step="any" inputmode="decimal" placeholder="依所選口徑填入"></label><label>每單位售價（元）<input name="price" type="number" min="0" step="any" inputmode="decimal" placeholder="本場實價"></label><label>節省飼料（kg）<input name="feed" type="number" min="0" step="any" inputmode="decimal" placeholder="同批差額"></label><label>飼料單價（元/kg）<input name="feed_price" type="number" min="0" step="any" inputmode="decimal" placeholder="本場實價"></label><label>本批方案投入（元）<input name="investment" type="number" min="0" step="any" inputmode="decimal" placeholder="本批總額"></label></div><div class="roi-result"><span>試算投資報酬率</span><output aria-live="polite">—%</output></div><p class="roi-note">先填本場數據；不同物種、週期與售價口徑分開計算。輸入值不會上傳。</p></form></section>'''


def page(path: str, title: str, description: str, body: str, image: str | None = None) -> None:
    rel = path.removesuffix("index.html")
    canonical = SITE + "/" + rel
    simplified_url = SITE + "/zh-cn/" + rel
    image = image or VIDEO + "/assets/p/brand-v05-v3-h.jpg"
    nav = '<a href="/">首頁</a><a href="/technology.html">核心技術</a><a href="/products/">產品線</a><a href="/stories.html">影音故事</a>'
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": title,
                         "url": canonical, "description": description,
                         "isPartOf": {"@type": "WebSite", "name": "活力得®", "url": SITE + "/"}}, ensure_ascii=False)
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="zh-Hant" href="{canonical}"><link rel="alternate" hreflang="zh-Hans" href="{simplified_url}"><meta property="og:type" content="website"><meta property="og:locale" content="zh_TW"><meta property="og:site_name" content="活力得®"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/huolide-mark.png"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script><script type="application/ld+json">{schema}</script></head><body><a class="skip" href="#main">跳至內容</a><header class="site-header"><a class="brand" href="/" aria-label="活力得®首頁"><img src="/assets/huolide-mark.png" alt="活力得®註冊圖形商標"><span>活力得<sup>®</sup><small>HUOLIDE · ANIMAL NUTRITION</small></span></a><nav aria-label="主要導覽">{nav}</nav><a class="header-action" href="/#roi">試算 ROI ↗</a></header><main id="main">{body}</main><footer><div class="footer-top"><div class="footer-brand"><img src="/assets/huolide-mark.png" alt="活力得®圖形商標"><div><strong>活力得<sup>®</sup></strong><p>重組蛋白酶與活性游離硅的單一複合功能材料</p></div></div><div class="footer-links"><a href="/technology.html">材料技術</a><a href="/products/">六條產品線</a><a href="/stories.html">影音故事</a><a href="{VIDEO}/">完整影音館</a><a href="{simplified_url}" lang="zh-Hans">简体中文</a></div></div><div class="footer-bottom"><span>活力得® 註冊商標 · 第 36751031 號</span><span>獸醫師 · 飼料配方師 · 農場經營者</span></div></footer></body></html>'''
    out = ROOT / (path or "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    simplified = TO_SIMPLIFIED.convert(html)
    simplified = simplified.replace('lang="zh-Hant"', 'lang="zh-Hans"', 1)
    simplified = simplified.replace(f'<link rel="canonical" href="{canonical}">', f'<link rel="canonical" href="{simplified_url}">', 1)
    simplified = simplified.replace(f'<meta property="og:url" content="{canonical}">', f'<meta property="og:url" content="{simplified_url}">', 1)
    simplified = simplified.replace('content="zh_TW"', 'content="zh_CN"', 1)
    simplified = simplified.replace(f'"url": "{canonical}"', f'"url": "{simplified_url}"', 1)
    simplified = simplified.replace(f'<a href="{simplified_url}" lang="zh-Hans">简体中文</a>', f'<a href="{canonical}" lang="zh-Hant">繁體中文</a>')
    simplified = re.sub(r'href="/(?!assets/|zh-cn/)', 'href="/zh-cn/', simplified)
    simplified_out = ROOT / "zh-cn" / (path or "index.html")
    simplified_out.parent.mkdir(parents=True, exist_ok=True)
    simplified_out.write_text(simplified, encoding="utf-8")


def product_card(product: tuple) -> str:
    slug, name, audience, _, _, videos = product
    story = PRODUCT_STORIES[slug]
    first = videos[0][1]
    return f'''<a class="product-card" href="/products/{slug}.html"><div class="product-film"><video class="motion-preview" muted loop playsinline preload="none" poster="{VIDEO}/assets/t/{first}.jpg" data-preview="{MEDIA}/{first}-hero-h.mp4" aria-hidden="true"></video><span class="product-index">{escape(audience)}</span></div><div class="product-card-copy"><div><h3>{escape(name)}</h3><p>{escape(story['hook'])}</p></div><div class="product-stat"><strong>{escape(story['value'])}</strong><span>{escape(story['metric'])}</span></div><span class="product-arrow">探索產品與影片 ↗</span></div></a>'''


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


def build() -> None:
    product_cards = "".join(product_card(product) for product in data.PRODUCTS)
    stats = "".join(
        f'<a href="/products/{slug}.html"><span>{escape(PRODUCT_STORIES[slug]["metric"])}</span><strong>{escape(PRODUCT_STORIES[slug]["value"])}</strong><small>{escape(PRODUCT_STORIES[slug]["source"])}</small></a>'
        for slug in ("junzaiwang", "zhangbiaowang", "zujinwang", "baomiaowang")
    )
    home = f'''<section class="hero wrap"><div class="hero-copy"><p class="kicker">活力得® / 飼料添加劑 · 單一複合材料</p><h1>同樣的料，<br><em>為什麼隔壁欄<br>賺更多？</em></h1><p>從蛋白質利用到骨、蹄、殼的結構支持。把能測的生產指標、可售產出與投入，放進同一張經營表。</p><div class="hero-actions"><a class="button solid" href="/products/">看六條產品線 ↗</a><a class="button outline" href="#roi">試算本場 ROI ↘</a></div><p class="hero-audience">獸醫師 / 飼料配方師 / 農場經營者</p></div>{hero_video('brand-v05-v3-h', '活力得品牌故事', VIDEO+'/v/brand-v05/', True)}</section><section class="proof-strip"><div class="wrap"><div class="proof-heading"><p class="kicker">從簡報數據，走向本場驗證</p><h2>數字要能回到<br>物種與批次。</h2></div><div class="proof-grid">{stats}</div></div></section><section class="section-products wrap"><div class="section-head inline"><div><p class="kicker">六條產品線 / 已發布影片</p><h2>每一條產品，<br>都有自己的生產問題。</h2></div><a class="text-link" href="/products/">按物種與階段瀏覽 ↗</a></div><div class="product-grid">{product_cards}</div></section>{species_gallery()}<section class="tech-feature"><div class="wrap"><div><p class="kicker">材料技術</p><h2>以單一複合材料軸心，<br>串連蛋白利用與結構營養。</h2><p>重組 C 系絲氨酸蛋白酶處理飼料蛋白；游離硅相關組分對應膠原、骨與殼的結構營養。從連續流反應器到逐批品質紀錄，讓配方判斷有清楚的技術脈絡。</p><a class="button outline" href="/technology.html">閱讀技術與製程 ↗</a></div>{hero_video('sci-v02', '連續流反應器與製程', VIDEO+'/v/sci-v02/')}</div></section>{roi_calculator()}'''
    page("", "活力得®｜重組蛋白酶與游離硅飼料添加劑・產品數據與 ROI", "活力得®動物營養材料：從台灣場域簡報數據、六條產品線與影片，了解母豬、蛋雞、育肥豬、肉雞、魚蝦的生產指標並試算本場 ROI。", home)

    tech = f'''<section class="inner-hero wrap"><div><p class="kicker">材料技術 / 製程 / 品質</p><h1>蛋白質利用，<br><em>連接結構營養。</em></h1><p>活力得®以重組 C 系絲氨酸蛋白酶與游離硅相關組分，構成單一複合功能材料。獸醫師看組織，配方師看日糧，農場主看可售產出與投入。</p></div>{hero_video('sci-v02', '連續流反應器與製程', VIDEO+'/v/sci-v02/')}</section><section class="tech-panes wrap"><article><span>PROTEASE / 蛋白質利用</span><h2>重組蛋白酶</h2><p>絲氨酸蛋白酶以 Ser–His–Asp 催化三聯體參與蛋白水解，對應小肽與胺基酸供給。</p></article><article><span>SILICON / 結構營養</span><h2>活性游離硅</h2><p>游離硅相關組分連接膠原基質、骨礦化與殼部結構，與蛋白利用放在同一材料軸心。</p></article></section><section class="section-videos wrap"><div class="section-head inline"><div><p class="kicker">技術影音</p><h2>把製程和作用路徑看清楚。</h2></div></div><div class="video-grid">{video_card('sci-v02','sci-v02','同一台反應器，為什麼每一批都一樣？')}{video_card('sci-v03-r2','sci-v03-r2','硅不是加了就有用')}</div></section>'''
    page("technology.html", "活力得®核心技術｜重組蛋白酶與游離硅複合材料", "閱讀活力得®重組 C 系絲氨酸蛋白酶、游離硅材料與連續流製程，並觀看已發布技術影片。", tech)

    listing = f'''<section class="inner-title wrap"><p class="kicker">中國市場 / 依物種與階段</p><h1>六條產品，<em>對應不同生產帳。</em></h1><p>先找物種，再看 PSY、FCR、蛋殼、胸肉、育成率與可售苗量；每條產品都回到自身的批次與收益口徑。</p></section><section class="section-products wrap tight"><div class="product-grid">{product_cards}</div></section>{market_taxonomy()}{roi_calculator()}'''
    page("products/index.html", "活力得®六條飼料添加劑產品線｜豬禽牛羊魚蝦", "依物種與生產階段瀏覽活力得®六條產品線、產品數據、影片與本場 ROI 試算。", listing)

    ruminants = f'''<section class="inner-hero wrap"><div><p class="kicker">反芻動物 / 生產型態</p><h1>牛羊營養，<br><em>從採食到出欄。</em></h1><p>肉牛肉羊的育肥、奶牛奶羊的泌乳，各有不同的日糧、體況與收益口徑。重組蛋白酶與游離硅的複合材料軸心，連接蛋白利用與蹄部、骨架結構。</p><a class="button solid" href="#roi">用本場數據試算 ROI ↘</a></div>{hero_video('brand-v05-v3-h','活力得品牌故事',VIDEO+'/v/brand-v05/',True)}</section><section class="tech-panes wrap"><article><span>MEAT / 肉用</span><h2>肉牛・肉羊</h2><p>按同物種和育肥階段追蹤採食、日增重、終重、FCR、肢蹄與出欄價格。</p></article><article><span>DAIRY / 乳用</span><h2>奶牛・奶山羊</h2><p>將泌乳量、乳成分、體況、採食與肢蹄紀錄分開閱讀，不套用肉用動物的數值。</p></article></section>{roi_calculator()}'''
    page("products/ruminants.html", "牛羊飼料利用與結構營養｜活力得®", "依肉牛、肉羊、奶牛和奶山羊生產型態閱讀飼料利用、採食、泌乳或出欄指標與本場 ROI。", ruminants)

    for slug, name, audience, _, _, videos in data.PRODUCTS:
        story = PRODUCT_STORIES[slug]
        first = videos[0][1]
        side_stats = "".join(f'<div><strong>{escape(number)}</strong><span>{escape(label)}</span></div>' for number, label in story['secondary'])
        focus = "".join(f'<article><strong>{escape(label)}</strong><p>{escape(detail)}</p></article>' for label, detail in data.FIELD_FOCUS[slug])
        cards = "".join(video_card(*video) for video in videos)
        body = f'''<section class="inner-hero product-hero wrap"><div><p class="kicker">{escape(audience)} / 活力得®產品線</p><h1>{escape(name)}<em>{escape(story['hook'])}</em></h1><p>從獸醫評估、日糧設計到農場收益，讓一條產品線回答同一個場域問題。</p><div class="hero-actions"><a class="button solid" href="#numbers">看核心數據 ↘</a><a class="button outline" href="#roi">試算 ROI ↘</a></div></div>{hero_video(first,name+'產品影片',VIDEO+'/v/'+videos[0][0]+'/')}</section><section class="number-story wrap" id="numbers"><div class="number-big"><p class="kicker">場域數字 / {escape(name)}</p><strong>{escape(story['value'])}</strong><span>{escape(story['unit'])} · {escape(story['metric'])}</span><p>{escape(story['basis'])}</p><small>{escape(story['source'])}</small></div><div class="number-side"><h2>數字背後，<br>是可重算的生產帳。</h2>{side_stats}</div></section><section class="audience-section wrap"><div class="section-head"><p class="kicker">從三個專業視角閱讀</p><h2>同一批數據，<br>對應三種決策。</h2></div><div class="audience-grid"><article><span>VET / 獸醫師</span><p>{escape(story['vet'])}</p></article><article><span>FORMULATION / 配方師</span><p>{escape(story['formulator'])}</p></article><article><span>FARM / 農場主</span><p>{escape(story['farmer'])}</p></article></div></section><section class="field-section wrap"><div><p class="kicker">田間紀錄 / 比較口徑</p><h2>把優勢寫進<br>同批次紀錄。</h2></div><div class="field-grid">{focus}</div></section>{roi_calculator()}<section class="section-videos wrap"><div class="section-head inline"><div><p class="kicker">{escape(name)} / 已發布影音</p><h2>看現場問題，<br>再看材料解法。</h2></div><a class="text-link" href="{VIDEO}/p/{slug}/">完整產品影音頁 ↗</a></div><div class="video-grid">{cards}</div></section>'''
        page(f"products/{slug}.html", f"{name}｜{audience}生產數據與 ROI｜活力得®", f"{name}對應{audience}。閱讀{story['metric']}、場域比較口徑、獸醫與配方視角，觀看已發布影片並試算本場 ROI。", body, f"{VIDEO}/assets/t/{first}.jpg")

    featured = [data.PRODUCTS[0][5][0], data.PRODUCTS[1][5][0], data.PRODUCTS[3][5][1], data.PRODUCTS[4][5][2], data.PRODUCTS[5][5][0]]
    stories = f'''<section class="inner-title wrap"><p class="kicker">活力得® / 影音故事</p><h1>每個數字背後，<em>都有一個現場問題。</em></h1><p>從產房、蛋雞舍、育肥場到養殖池，影片以生產問題連接技術與產品。完整版、旁白和更多分類都在影音館。</p><a class="button solid" href="{VIDEO}/">進入影音館 ↗</a></section><section class="section-videos wrap"><div class="video-grid">{''.join(video_card(*video) for video in featured)}</div></section>'''
    page("stories.html", "活力得®影音故事｜豬禽水產產品影片", "觀看活力得®豬禽水產產品影片、現場問題與技術故事。", stories)

    for old, destination in data.OLD_ROUTES.items():
        target = f"{SITE}/{destination}"
        dest = ROOT / old
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{target}"><title>頁面已移至活力得®新站</title></head><body><a href="{target}">前往新版頁面</a></body></html>', encoding="utf-8")
    routes = ["", "technology.html", "products/", "stories.html", "products/ruminants.html"] + [f"products/{p[0]}.html" for p in data.PRODUCTS]
    all_routes = routes + [f"zh-cn/{route}" for route in routes]
    today = date.today().isoformat()
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}/{route}</loc><lastmod>{today}</lastmod></url>\n" for route in all_routes) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    media_sources = {"source_site": VIDEO + "/", "public_r2_base": MEDIA + "/",
                     "brand": {"watch_page": VIDEO + "/v/brand-v05/", "video": MEDIA + "/brand-v05-v3-h.mp4", "preview": MEDIA + "/brand-v05-v3-hero-h.mp4"},
                     "products": [{"slug": slug, "name": name, "source_page": f"{VIDEO}/p/{slug}/",
                                   "videos": [{"watch_page": f"{VIDEO}/v/{video_slug}/", "r2_video": f"{MEDIA}/{object_name}.mp4", "preview": f"{MEDIA}/{object_name}-hero-h.mp4", "poster": f"{VIDEO}/assets/t/{object_name}.jpg", "topic": title}
                                              for video_slug, object_name, title in videos]}
                                  for slug, name, _, _, _, videos in data.PRODUCTS]}
    (ROOT / "media-sources.json").write_text(json.dumps(media_sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BUILD OK pages={len(all_routes)} legacy_redirects={len(data.OLD_ROUTES)} sitemap_urls={len(all_routes)} logo=huolide-mark.png")


if __name__ == "__main__":
    build()
