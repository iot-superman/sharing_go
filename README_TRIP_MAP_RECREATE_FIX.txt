共乘 Go - iPhone 12 mini 行程路線「重建一次」穩定版

你最新截圖的判斷：
- 底圖只出現左上角一塊藍色/海色 tile
- 距離時間仍顯示 2.84 km / 5 分鐘
=> OSRM 有成功，問題仍是 Leaflet 在 iOS WebView 取得錯誤容器尺寸。

這次不再用「不停修同一張 Leaflet map」的方法。

新策略：
1. 每 2 秒 refresh 只更新文字/成員，不碰 Leaflet。
2. 只有你真正點進「行程」Tab 時：
   - 等兩個 animation frame
   - 再等 120ms
   - destroy 舊 map
   - 用目前可見且已完成 layout 的容器重新 new L.map()
   - 畫 route
   - 最後 fitBounds
3. 停留在行程頁期間不再重建，因此不抖。
4. 手機 map 高度改用 aspect-ratio:16/9，不再用 dvh。
   iPhone Safari / LINE 的網址列收合不會再影響地圖高度。
5. 若重新切出/切回行程頁，會再重建一次，確保尺寸正確。

這是比 invalidateSize + visualViewport watcher 更保守也更穩定的方式。
