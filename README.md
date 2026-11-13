# richtrong.com 活力得® 品牌站

此 repo 的 `main` 分支由 GitHub Pages 提供 `richtrong.com`。`v.feed-pet.com` 是獨立的正式影音館，影片由公開 R2 網域 `media.feed-pet.com` 提供；本站只引用已發布網址，不修改影音館或 R2 物件。

## 網站架構

- 首頁：材料定位、品牌影片、六條產品線
- `/technology.html`：重組蛋白酶與活性游離硅的材料脈絡
- `/products/`：中國市場依物種與階段瀏覽，再看六條產品線
- `/products/*.html`：六條產品線及肉牛／肉羊應用頁
- `/stories.html`：跨物種影片精選
- 舊方案檔名：保留為 `noindex` 跳轉頁，導向目前的物種／產品頁

網站以「活力得®」為唯一對外品牌。舊品牌字串只存在於歷史網址對照表的檔名中，供原連結跳轉使用。`FCR_benchmark.jpg` 用於規劃物種分類；圖內的跨物種 FCR 數字與排名沒有直接上站。

## 更新方式

編輯 `build_site.py` 中的產品、物種與影片清單後執行：

```powershell
python -X utf8 D:\LLM\sites\feed\build_site.py
```

產物含 HTML、sitemap、robots 與 `media-sources.json`（公開來源頁、R2 影片及海報圖完整網址）。發佈前檢查舊品牌字樣、連結 HTTP 狀態、手機橫向溢出及正式站發布閘；`main` 分支推送會更新 GitHub Pages。
