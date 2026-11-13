"""Build the static richtrong.com editorial site from the approved video URLs."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re

ROOT = Path(__file__).resolve().parent
SITE = "https://richtrong.com"
VIDEO = "https://v.feed-pet.com"
MEDIA = "https://media.feed-pet.com"
TODAY = date.today().isoformat()

# Titles and immutable R2 object names were read from the published video site.
PRODUCTS = [
    ("junzaiwang", "均仔旺", "母豬與仔豬", "從母豬營養到仔豬離乳，閱讀產房與保育階段的產品故事。", "n_sow.jpg", [
        ("p1-v01", "p1-v01-v1", "同一窩仔豬有胖有瘦？"), ("p1-v02", "p1-v02-v1", "母豬年產斷奶仔豬的營養管理"), ("p1-v03", "p1-v03-v1", "母豬蹄部與骨架的營養支持"), ("p1-v04", "p1-v04-v1", "弱仔與整窩離乳管理"),
    ]),
    ("keliwang", "殼力旺", "蛋雞與蛋殼", "聚焦蛋殼品質、產蛋高峰與蛋雞營養。", "n_layer.jpg", [
        ("p2-v01", "p2-v01-v2", "蛋殼品質與破損管理"), ("p2-v02", "p2-v02-v2", "產蛋高峰期的營養支持"), ("p2-v03", "p2-v03-v2", "蛋黃與產蛋表現"), ("p2-v04", "p2-v04-v2", "老母雞穩產管理"), ("p2-v06", "p2-v06-v2", "蛋品營養與賣相"),
    ]),
    ("duoluanzhuang", "多卵壯", "水產親本與種苗", "從親魚營養到受精、孵化與種苗整齊度。", "n_breeder.jpg", [
        ("p3-v01", "p3-v01-v1", "親本受精率的管理"), ("p3-v02", "p3-v02-v1", "種苗整齊度"), ("p3-v03", "p3-v03-v2", "親魚繁殖週期"), ("p3-v04", "p3-v04-v1", "高值魚苗受精管理"), ("p3-v05", "p3-v05-v1", "孵化與苗期活力"), ("p3-v06", "p3-v06-v1", "種苗存活管理"),
    ]),
    ("zhangbiaowang", "長膘旺", "育肥豬", "以肉質、料效與出欄整齊度為主題。", "n_pig.jpg", [
        ("p4-v01", "p4-v01-v1", "背膘與腰肌眼的管理"), ("p4-v02", "p4-v02-v1", "從糞篩觀察飼料利用"), ("p4-v03", "p4-v03-v1", "骨架與生長節奏"), ("p4-v04", "p4-v04-v1", "瘦肉率與肉質"),
    ]),
    ("zujinwang", "足斤旺", "肉雞", "關注蛋白質利用、體重與胸肉表現。", "n_broiler.jpg", [
        ("p5-v01", "p5-v01-v1", "料肉比與利潤"), ("p5-v02", "p5-v02-v1", "肉雞出欄體重"), ("p5-v03", "p5-v03-v1", "胸肉產量"), ("p5-v04", "p5-v04-v1", "豆粕蛋白與抗營養因子"),
    ]),
    ("baomiaowang", "保苗旺", "魚蝦養殖", "涵蓋苗期育成、規格整齊與蝦殼礦化。", "n_aqua.jpg", [
        ("p6-v01", "p6-v01-v2", "苗期育成管理"), ("p6-v02", "p6-v02-v1", "蝦苗規格整齊度"), ("p6-v03", "p6-v03-v2", "脫殼與礦化"), ("p6-v04", "p6-v04-v1", "魚苗存活與生長"),
    ]),
]

SPECIES = {
    "junzaiwang": ("母豬", "哺乳仔豬", "離乳仔豬"),
    "keliwang": ("蛋雞", "種雞"),
    "duoluanzhuang": ("親魚", "魚卵", "魚苗"),
    "zhangbiaowang": ("育肥豬",),
    "zujinwang": ("肉雞",),
    "baomiaowang": ("蝦苗", "白蝦", "養成魚"),
}

OLD_ROUTES = {
    "swine-breeding.html": "products/junzaiwang.html",
    "活力旺種公豬精液品質提升方案.html": "products/junzaiwang.html",
    "活力旺懷孕期母豬生產性能優化方案.html": "products/junzaiwang.html",
    "活力旺哺乳母豬性能提升方案.html": "products/junzaiwang.html",
    "活力旺仔豬人工乳性能提升方案.html": "products/junzaiwang.html",
    "活力旺育肥豬性能提升方案.html": "products/zhangbiaowang.html",
    "活力旺育肥豬FCR性能提升方案.html": "products/zhangbiaowang.html",
    "活力旺蛋雞性能提升方案.html": "products/keliwang.html",
    "活力旺種雞性能提升方案.html": "products/duoluanzhuang.html",
    "活力旺土雞性能提升方案.html": "products/zujinwang.html",
    "活力旺白肉雞FCR性能提升方案.html": "products/zujinwang.html",
    "活力旺白蝦存活率提升方案.html": "products/baomiaowang.html",
    "活力旺吳郭魚存活率提升方案.html": "products/baomiaowang.html",
    "活力旺羅氏沼蝦性能提升方案.html": "products/baomiaowang.html",
}


def tag(title: str, text: str, href: str, cls: str = "") -> str:
    return f'<a class="{cls}" href="{escape(href, quote=True)}"><span>{escape(title)}</span><small>{escape(text)}</small><b aria-hidden="true">↗</b></a>'


def video_card(slug: str, object_name: str, title: str) -> str:
    poster = f"{VIDEO}/assets/t/{object_name}.jpg"
    return f'''<article class="video-card"><a href="{VIDEO}/v/{slug}/" aria-label="觀看：{escape(title, quote=True)}"><img src="{poster}" alt="{escape(title, quote=True)}" loading="lazy" width="640" height="360"><span class="play" aria-hidden="true">▶</span></a><div><h3>{escape(title)}</h3><a class="text-link" href="{VIDEO}/v/{slug}/">觀看影片與旁白 <span aria-hidden="true">↗</span></a></div></article>'''


def science_card(slug: str, title: str) -> str:
    return f'''<article class="video-card"><video controls playsinline preload="none" poster="{VIDEO}/assets/t/{slug}.jpg" aria-label="{escape(title, quote=True)}"><source src="{MEDIA}/{slug}.mp4" type="video/mp4">您的瀏覽器不支援影片播放。</video><div><h3>{escape(title)}</h3><a class="text-link" href="{VIDEO}/#tech">前往影音館技術專區 ↗</a></div></article>'''


def page(path: str, title: str, description: str, body: str, image: str = f"{VIDEO}/assets/p/brand-v05-v3-h.jpg") -> None:
    canonical_path = path.removesuffix("index.html")
    canonical = f"{SITE}/{canonical_path}" if canonical_path else f"{SITE}/"
    active = "products" if path.startswith("products/") else path.split(".")[0]
    nav = "".join(f'<a href="/{href}"{(" aria-current=\"page\"" if active == key else "")}>{label}</a>' for key, href, label in [
        ("index", "", "首頁"), ("technology", "technology.html", "核心技術"), ("products", "products/", "產品線"), ("stories", "stories.html", "影音故事")
    ])
    schema = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": canonical, "description": description, "isPartOf": {"@type": "WebSite", "name": "活力得®", "url": SITE + "/"}}, ensure_ascii=False)
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:locale" content="zh_TW"><meta property="og:site_name" content="活力得®"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{VIDEO}/assets/logo.png"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{schema}</script></head><body><a class="skip" href="#main">跳至主要內容</a><header class="site-header"><a class="brand" href="/" aria-label="活力得首頁"><span class="brand-mark">H<span>·</span></span><span>活力得<sup>®</sup><small>HUOLIDE</small></span></a><nav aria-label="主要導覽">{nav}</nav><a class="header-video" href="{VIDEO}/">進入影音館 <span aria-hidden="true">↗</span></a></header><main id="main">{body}</main><footer><div><strong>活力得<sup>®</sup></strong><p>重組蛋白酶與活性游離硅的複合功能材料</p></div><div class="footer-links"><a href="/technology.html">核心技術</a><a href="/products/">產品線</a><a href="/stories.html">影音故事</a><a href="{VIDEO}/">完整影音館</a></div><p class="legal">活力得® 為註冊商標（第 36751031 號）。</p></footer></body></html>'''
    out = ROOT / path if path else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build() -> None:
    product_links = "".join(tag(name, audience, f"/products/{slug}.html", "product-tile") for slug, name, audience, *_ in PRODUCTS)
    hero = f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">HUOLIDE · 動物營養材料</p><h1>把營養的利用，<em>做進結構裡。</em></h1><p class="lead">活力得®以重組蛋白酶與活性游離硅構成複合功能材料，從蛋白質利用到組織結構支持，連接豬、禽與水產的營養需求。</p><div class="actions"><a class="button primary" href="/technology.html">了解核心技術 <span aria-hidden="true">↗</span></a><a class="button quiet" href="{VIDEO}/v/brand-v05/">觀看品牌故事 ▶</a></div><div class="hero-caption"><span>01 / 蛋白質利用</span><span>02 / 結構支持</span><span>03 / 物種應用</span></div></div><div class="hero-media"><video controls playsinline preload="none" poster="{VIDEO}/assets/p/brand-v05-v3-h.jpg" aria-label="活力得品牌故事"><source src="{MEDIA}/brand-v05-v3-h.mp4" type="video/mp4">您的瀏覽器不支援影片播放。</video><a href="{VIDEO}/v/brand-v05/">觀看完整影片與旁白 ↗</a></div></section>'''
    home = hero + f'''<section class="statement"><p class="eyebrow">同一材料 · 兩條作用路徑</p><h2>一端處理蛋白質，<br>一端支持組織構造。</h2><div class="path-grid"><article><span class="path-number">A</span><h3>重組蛋白酶</h3><p>以絲氨酸蛋白酶的催化結構為技術核心，聚焦飼料蛋白的水解與利用。</p></article><article><span class="path-number">B</span><h3>活性游離硅</h3><p>以可利用單體硅為材料方向，連接膠原與骨、殼等結構的營養支持。</p></article></div><a class="text-link" href="/technology.html">閱讀技術脈絡 ↗</a></section><section class="product-section"><div class="section-heading"><div><p class="eyebrow">依物種與生產階段尋找</p><h2>六條產品線</h2></div><a class="text-link" href="/products/">查看全部產品 ↗</a></div><div class="product-grid">{product_links}</div></section><section class="feature"><div><p class="eyebrow">影像與文字，同一個故事</p><h2>從製程到田間，<br>看見每個問題怎麼被拆解。</h2><p>已發布影片有逐片獨立頁、字幕與旁白。從一個生產問題開始，閱讀技術背景，再觀看對應的產品故事。</p><a class="button primary" href="/stories.html">探索影音故事 ↗</a></div><img src="{VIDEO}/assets/t/sci-v02.jpg" alt="活力得技術科普影片畫面" loading="lazy" width="720" height="405"></section>'''
    page("", "活力得®｜重組蛋白酶與活性游離硅的動物營養材料", "活力得®以重組蛋白酶與活性游離硅為核心，介紹豬、禽、水產的產品線、技術脈絡與已發布影音故事。", home)

    tech = f'''<section class="page-intro"><p class="eyebrow">材料科學 / 核心技術</p><h1>從蛋白質利用，<br><em>走向組織結構。</em></h1><p>活力得®的複合材料軸心結合重組 C-鑒系絲氨酸蛋白酶與活性游離硅。科學總論從兩條路徑說明材料設計，再延伸到不同物種的營養場景。</p></section><section class="science-layout"><article><span>01 / ENZYME</span><h2>重組蛋白酶</h2><p>絲氨酸蛋白酶以 Ser–His–Asp 催化三聯體參與蛋白質水解。產品敘事聚焦大分子蛋白、小肽與氨基酸的利用路徑。</p></article><article><span>02 / SILICON</span><h2>活性游離硅</h2><p>游離硅相關組分對應結構營養方向；科學總論將其與膠原基質、骨礦化及殼部結構連結。</p></article><article><span>03 / COMPLEX</span><h2>複合材料軸心</h2><p>以同一材料設計連結軟組織的營養利用與硬組織的結構支持，並按物種和生產階段呈現應用。</p></article></section><section class="media-block"><div><p class="eyebrow">技術影片</p><h2>看見材料的工作方式</h2><p>觀看反應器與機轉的已發布科普影片，或前往影音館閱讀完整內容。</p><a class="text-link" href="{VIDEO}/">瀏覽全部技術影片 ↗</a></div><div class="video-grid">{science_card('sci-v02','連續流反應器與製程')}{science_card('sci-v03-r2','科學機轉與材料設計')}</div></section>'''
    page("technology.html", "核心技術｜重組蛋白酶與活性游離硅｜活力得®", "了解活力得®的重組 C-鑒系絲氨酸蛋白酶、活性游離硅與複合材料軸心，並觀看已發布的製程與機轉影片。", tech)

    market_cards = "".join(tag(label, detail, href, "product-tile") for label, detail, href in [
        ("母豬・仔豬", "繁殖、哺乳與離乳階段", "/products/junzaiwang.html"),
        ("育肥豬", "生長、料效與出欄", "/products/zhangbiaowang.html"),
        ("肉牛・肉羊", "反芻動物育肥與結構營養", "/products/ruminants.html"),
        ("蛋雞・種雞", "蛋殼、產蛋與親本", "/products/keliwang.html"),
        ("肉雞", "蛋白質利用與出欄", "/products/zujinwang.html"),
        ("魚・蝦", "親本、種苗與育成", "/products/baomiaowang.html"),
    ])
    listing = f'''<section class="page-intro"><p class="eyebrow">中國市場 / 依物種與生產階段瀏覽</p><h1>先找物種，<br><em>再找營養問題。</em></h1><p>從豬、家禽、反芻牛羊到魚蝦，先按養殖對象找頁面。不同物種與階段的飼料轉換率不能直接混為同一基準；閱讀時請先確認比較口徑。</p></section><section class="product-section"><div class="section-heading"><div><p class="eyebrow">物種應用</p><h2>六個養殖入口</h2></div></div><div class="product-grid">{market_cards}</div><p class="market-note">家禽延伸場景包含鴨、鵝；反芻動物包含奶牛、山羊等不同生產型態。本站以目前已有專頁內容的物種與階段作導覽，跨物種的 FCR 數值需按飼養條件分別閱讀。</p></section><section class="product-section"><div class="section-heading"><div><p class="eyebrow">活力得® / 已發布產品影音</p><h2>六條產品線</h2></div></div><div class="product-grid">{product_links}</div></section>'''
    page("products/index.html", "豬禽牛羊魚蝦營養與六條產品線｜活力得®", "依母豬仔豬、育肥豬、肉牛肉羊、蛋雞種雞、肉雞與魚蝦養殖瀏覽活力得®產品線及已發布影片。", listing)
    ruminants = '''<section class="page-intro"><p class="eyebrow"><a href="/products/">物種應用</a> / 反芻動物</p><h1>肉牛與肉羊<em>｜育肥與結構營養</em></h1><p>反芻動物的營養管理要同時看採食、消化利用、日增重與肢蹄結構。活力得®科學總論及反芻專題簡報以重組蛋白酶和游離硅的複合材料軸心，討論這兩條營養路徑。</p><div class="actions"><a class="button primary" href="/technology.html">閱讀材料技術 ↗</a><a class="button quiet" href="/products/">查看其他物種</a></div></section><section class="science-layout"><article><span>01 / CATTLE</span><h2>肉牛</h2><p>從育肥階段的飼料利用、日增重與出欄體況整理營養問題。</p></article><article><span>02 / SHEEP</span><h2>肉羊</h2><p>從採食、育肥與肢蹄支撐切入，按飼養階段閱讀材料應用。</p></article><article><span>03 / FCR</span><h2>比較口徑</h2><p>FCR 是飼料投入與增重的比值。牛羊、豬與禽類的生理及飼養週期不同，需在同物種、同階段、同口徑下比較。</p></article></section>'''
    page("products/ruminants.html", "肉牛肉羊營養與飼料利用｜活力得®", "按肉牛和肉羊育肥階段閱讀飼料利用、日增重、肢蹄結構與活力得®複合材料的技術脈絡。", ruminants)
    for slug, name, audience, description, _, videos in PRODUCTS:
        cards = "".join(video_card(*item) for item in videos)
        species = "".join(f"<span>{escape(label)}</span>" for label in SPECIES[slug])
        body = f'''<section class="page-intro"><p class="eyebrow"><a href="/products/">物種應用</a> / {escape(audience)}</p><h1>{escape(name)}<em>｜{escape(audience)}</em></h1><p>{escape(description)}活力得®以重組蛋白酶與活性游離硅為共同材料軸心，依生產階段展開應用。</p><div class="species-list" aria-label="對應物種與階段">{species}</div><div class="actions"><a class="button primary" href="{VIDEO}/p/{slug}/">進入{escape(name)}影音專頁 ↗</a><a class="button quiet" href="/technology.html">閱讀核心技術</a></div></section><section class="media-block"><div><p class="eyebrow">{len(videos)} 部已發布影片</p><h2>從現場問題開始看</h2><p>每支影片的完整版與旁白，均保存在活力得®影音館的獨立頁面。</p></div><div class="video-grid">{cards}</div></section><section class="next"><p>繼續探索</p><a href="/products/">其他物種與產品 ↗</a><a href="/technology.html">材料技術 ↗</a></section>'''
        page(f"products/{slug}.html", f"{name}｜{audience}營養｜活力得®", f"{name}聚焦{audience}。閱讀活力得®重組蛋白酶與活性游離硅的材料背景，觀看{len(videos)}部已發布產品影片。", body, f"{VIDEO}/assets/t/{videos[0][1]}.jpg")

    featured = [PRODUCTS[0][5][0], PRODUCTS[1][5][0], PRODUCTS[3][5][1], PRODUCTS[4][5][3], PRODUCTS[5][5][2]]
    stories = f'''<section class="page-intro"><p class="eyebrow">故事 / 已發布影片</p><h1>一個問題，<br><em>一段可追的故事。</em></h1><p>從田間的營養問題切入，延伸到材料與產品的具體應用。這裡精選影片；所有完整版、旁白與產品分類請到影音館觀看。</p><a class="button primary" href="{VIDEO}/">進入完整影音館 ↗</a></section><section class="media-block"><div><p class="eyebrow">影片精選</p><h2>從豬、禽到魚蝦</h2></div><div class="video-grid">{''.join(video_card(*v) for v in featured)}</div></section>'''
    page("stories.html", "影音故事｜活力得®豬禽水產產品影片", "探索活力得®的豬、禽、水產產品影片與技術科普，前往影音館觀看完整版、字幕和旁白。", stories)

    for old, destination in OLD_ROUTES.items():
        target = f"{SITE}/{destination}"
        (ROOT / old).write_text(f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{target}"><title>頁面已移至活力得®新站</title></head><body><p>此內容已更新。<a href="{target}">前往新版頁面</a></p></body></html>', encoding="utf-8")

    routes = ["", "technology.html", "products/", "stories.html", "products/ruminants.html"] + [f"products/{p[0]}.html" for p in PRODUCTS]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}/{route}</loc><lastmod>{TODAY}</lastmod></url>\n" for route in routes) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    media_sources = {
        "source_site": VIDEO + "/",
        "public_r2_base": MEDIA + "/",
        "brand": {"watch_page": VIDEO + "/v/brand-v05/", "video": MEDIA + "/brand-v05-v3-h.mp4"},
        "science": [
            {"name": slug, "video": f"{MEDIA}/{slug}.mp4", "poster": f"{VIDEO}/assets/t/{slug}.jpg"}
            for slug in ("sci-v02", "sci-v03-r2")
        ],
        "products": [
            {"slug": slug, "name": name, "source_page": f"{VIDEO}/p/{slug}/", "videos": [
                {"watch_page": f"{VIDEO}/v/{video_slug}/", "r2_video": f"{MEDIA}/{object_name}.mp4", "poster": f"{VIDEO}/assets/t/{object_name}.jpg", "topic": title}
                for video_slug, object_name, title in videos
            ]}
            for slug, name, _, _, _, videos in PRODUCTS
        ],
    }
    (ROOT / "media-sources.json").write_text(json.dumps(media_sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BUILD OK pages={len(routes)} legacy_redirects={len(OLD_ROUTES)} sitemap_urls={len(routes)}")


if __name__ == "__main__":
    build()
