"""Build the static richtrong.com editorial site from the approved video URLs."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re
from opencc import OpenCC

ROOT = Path(__file__).resolve().parent
SITE = "https://richtrong.com"
VIDEO = "https://v.feed-pet.com"
MEDIA = "https://media.feed-pet.com"
TODAY = date.today().isoformat()
TO_SIMPLIFIED = OpenCC("t2s")

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
    "junzaiwang": ("哺乳母豬", "哺乳仔豬", "保育仔豬"),
    "keliwang": ("蛋雞",),
    "duoluanzhuang": ("親魚", "魚卵", "魚苗"),
    "zhangbiaowang": ("育肥豬",),
    "zujinwang": ("白羽肉雞", "黃羽肉雞"),
    "baomiaowang": ("蝦苗", "養殖蝦", "養殖魚"),
}

# Product-specific editorial content distilled from the current D1-D6 PPT
# themes and old site headings. These are measurement topics, not efficacy data.
FIELD_FOCUS = {
    "junzaiwang": (
        ("產房", "記錄母豬採食、哺乳狀態與同窩仔豬初生重差異。"),
        ("保育", "追蹤離乳重、均勻度、日糧攝取與保育階段增重。"),
        ("比較", "用同一農場、胎次與離乳日齡建立批次比較口徑。"),
    ),
    "keliwang": (
        ("蛋殼", "追蹤蛋殼厚度、破損率與商品蛋分級。"),
        ("產蛋", "分別記錄產蛋高峰及後期的產蛋率和蛋重。"),
        ("日糧", "同步記錄採食量、鈣磷來源與飼養週齡。"),
    ),
    "duoluanzhuang": (
        ("親本", "按魚種及繁殖週期記錄親魚體況與產卵批次。"),
        ("孵化", "分開追蹤受精率、孵化率與苗期規格整齊度。"),
        ("水質", "同步保存水溫、溶氧與放養密度等養殖條件。"),
    ),
    "zhangbiaowang": (
        ("育肥", "以入欄重、出欄重、育肥天數與日增重建立批次紀錄。"),
        ("料效", "FCR 需配合飼料投入、活重增量及死亡淘汰口徑解讀。"),
        ("肉質", "依同一屠宰與測量方式記錄背膘和胴體指標。"),
    ),
    "zujinwang": (
        ("出欄", "按白羽與黃羽肉雞的品系和日齡分開追蹤體重。"),
        ("料效", "記錄各批次採食、增重與料肉比，避免跨品系直接比較。"),
        ("胴體", "依同一屠宰規格記錄胸肉與腿部表現。"),
    ),
    "baomiaowang": (
        ("苗期", "按魚種或蝦種記錄放苗規格、密度和存活率。"),
        ("養成", "追蹤日糧投入、規格分布與收成重量。"),
        ("環境", "把水質、鹽度及脫殼週期與生產紀錄一起檢視。"),
    ),
}

OLD_ROUTES = {
    "feed/fcr/index.html": "products/",
    "swine-breeding.html": "products/junzaiwang.html",
    "活力旺種公豬精液品質提升方案.html": "products/#pig",
    "活力旺懷孕期母豬生產性能優化方案.html": "products/junzaiwang.html",
    "活力旺哺乳母豬性能提升方案.html": "products/junzaiwang.html",
    "活力旺仔豬人工乳性能提升方案.html": "products/junzaiwang.html",
    "活力旺育肥豬性能提升方案.html": "products/zhangbiaowang.html",
    "活力旺育肥豬FCR性能提升方案.html": "products/zhangbiaowang.html",
    "活力旺蛋雞性能提升方案.html": "products/keliwang.html",
    "活力旺種雞性能提升方案.html": "products/#poultry",
    "活力旺土雞性能提升方案.html": "products/#poultry",
    "活力旺白肉雞FCR性能提升方案.html": "products/zujinwang.html",
    "活力旺白蝦存活率提升方案.html": "products/baomiaowang.html",
    "活力旺吳郭魚存活率提升方案.html": "products/baomiaowang.html",
    "活力旺羅氏沼蝦性能提升方案.html": "products/baomiaowang.html",
}
