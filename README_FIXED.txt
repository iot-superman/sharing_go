共乘 Go Django - 建立共乘 / 查地址 / 地圖自動切換修正版

這次修正兩個實際 Bug：

1. 上一版 UI 精簡時，把 JS 核心函式誤刪掉
   - searchAddress()
   - createRide()
   - joinRide()
   - cancelRide()
   所以 🔎 查地址按鈕與「建立共乘」會完全沒反應。
   本版已完整補回。

2. OSM 被 Blocked / 403 時自動切換 CARTO
   - OSM 第一個 tileerror 後短暫等待
   - 連續錯誤立即切換 CARTO Voyager
   - 不再跳 alert 阻塞操作，改用地圖左下角短暫提示
   - CARTO 若也失敗，會嘗試切回 OSM
   - 使用者仍可手動切換底圖

UI 保留：
- 地址欄右側只顯示 🔎 與 🗺️ icon
- 精確選工具列 icon-only
- iPhone / Android 手機版
- MQTT 即時聊天
- 即時定位
- 路線預覽
