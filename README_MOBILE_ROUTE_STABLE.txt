共乘 Go - 手機瀏覽器路線圖穩定版

這次確認：不只 iPhone 12 mini，POCO M4 Pro 等 Android 手機也可能出現同類問題。
所以根因不是單一 iPhone，而是 Leaflet 在「隱藏 Tab / 小尺寸 / 動態瀏覽器工具列」下的容器尺寸時序。

本版改成跨手機通用處理：
1. 真正進入「行程」Tab 後才重建路線地圖。
2. 連續檢查容器 width / height / offsetParent，尺寸可量測才 new L.map()。
3. 快速切換 Tab 時用 build sequence 取消舊的非同步建立流程。
4. 使用 IntersectionObserver，地圖真正進入 viewport 後再校正 fitBounds。
5. 行程頁停留期間，每 2 秒 refresh 不重建地圖，所以不會抖。
6. 手機地圖改用較穩定的 aspect-ratio；<=390px 改成接近正方形，避免 POCO/iPhone mini 太扁。
7. iOS / Android / LINE WebView / Chrome 都走同一套邏輯。

測試建議：
- iPhone 12 mini
- POCO M4 Pro
- Windows Chrome 縮到 375px 寬
- LINE 內建瀏覽器
