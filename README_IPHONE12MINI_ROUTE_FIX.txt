共乘 Go - iPhone 12 mini 行程路線圖 viewport 修正版

症狀
====
在 iPhone 12 mini / LINE WebView / 某些較窄長寬下：
- OSM 底圖正常
- 距離與時間有成功算出（代表 /api/route/ 有成功）
- 但藍色路線、起點旗子、Goal 會跑到目前可視範圍外
- 看起來像「路線沒有畫」

根因
====
Leaflet 在 iOS Safari / LINE WebView 中，
頂部/底部瀏覽器工具列會改變 visual viewport 高度。
地圖剛從 display:none 變成可見時，
clientWidth/clientHeight 可能還不是最終尺寸。

如果在這個瞬間 fitBounds：
Leaflet 會用錯誤的 viewport 尺寸計算中心/zoom。
之後即使 invalidateSize()，它只修正尺寸，
不會自動重新 fit 路線，所以底圖有了但路線在畫面外。

本版修正
========
1. route geometry 成功後把 route bounds 保存於 map。
2. 先 invalidateSize({pan:false})，再重新 fitBounds(route bounds)。
3. iPhone 12 mini 小尺寸使用較小 padding。
4. 監聽 ResizeObserver：容器寬高真的改變才 refit。
5. 監聽 visualViewport.resize：處理 Safari/LINE 地址列收合。
6. 監聽 orientationchange。
7. 進入行程頁後 100/280/650ms 多階段穩定 refit。
8. 每 2 秒資料 refresh 不做 fitBounds，所以不會重新抖動。
9. 手機地圖高度改為 clamp(210px, 30dvh, 280px)。

判斷重點
========
畫面若顯示：
  約 2.65 km・4 分鐘
代表 OSRM 路線資料其實已經成功。
本 bug 是 Leaflet viewport/fitBounds 時序，不是 OSRM 沒路線。
