# richtrong.com 活力得® 品牌站

此 repo 的 `main` 分支由 GitHub Pages 提供 `richtrong.com`。`v.feed-pet.com` 是獨立的正式影音館，影片由公開 R2 網域 `media.feed-pet.com` 提供；本站只引用已發布網址，不修改影音館或 R2 物件。頁面以無聲短預覽為主視覺，文字作導覽與搜尋索引。

## 網站架構

- 首頁：材料定位、品牌影片、六條產品線
- `/technology.html`：重組蛋白酶與活性游離硅的材料脈絡
- `/products/`：中國市場依物種與階段瀏覽，再看六條產品線
- `/products/*.html`：六條產品線及肉牛／肉羊應用頁
- `/stories.html`：跨物種影片精選
- 舊方案檔名：保留為 `noindex` 跳轉頁，導向目前的物種／產品頁
- `/zh-cn/`：上述 11 頁的簡體中文版；繁、簡頁各有 canonical 和互相對應的 hreflang

網站以「活力得®」為唯一對外品牌。舊品牌字串只存在於歷史網址對照表的檔名中，供原連結跳轉使用。`FCR_benchmark.jpg` 用於規劃物種分類；圖內的跨物種 FCR 數字與排名沒有直接上站。

## 更新方式

編輯 `build_site.py` 中的產品、物種與影片清單後執行。建置需要 Python 的 `opencc` 模組：

```powershell
python -X utf8 D:\LLM\sites\feed\build_site.py
```

產物含繁簡 HTML、sitemap、robots 與 `media-sources.json`（影音來源與 R2 正片／短預覽網址）。首頁 32 支影片及優先輪播比例規則見 [Hero 輪播 SSOT](docs/HERO_CAROUSEL_SSOT.md)。圖片採用清單、拒用案例與去重規範見 [視覺素材 SSOT](docs/VISUAL_ASSET_SSOT.md)；完整 SHA256 見 `assets/species/provenance.json`。`assets/site.js` 只在影片進入畫面時載入預覽，離開畫面暫停；首頁 Hero 逐輪播放全部影片，未載入影片時顯示對應場景圖。發佈前檢查舊品牌字樣、繁簡互鏈、連結 HTTP 狀態、手機橫向溢出及正式站發布閘；`main` 分支推送會更新 GitHub Pages。
