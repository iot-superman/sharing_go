共乘 Go - 行程頁地圖不抖動 + 不破圖修正版

這次修的問題：
前一版為了避免每 2 秒重畫地圖，把 Leaflet 地圖保留下來，
但 loadTrip() 可能在「行程」頁還是 display:none 時就先建立地圖。
Leaflet 在隱藏容器中初始化時拿不到正確寬高，所以 iPhone/Chrome
會出現只有上面一小條圖磚、下面整片灰色的狀況。

修正：
1. 行程小地圖只在「行程」頁真正可見時才初始化。
2. 切換到行程頁後做 2 次 invalidateSize()。
3. 若容器寬高尚未完成 layout，延遲 150ms 再建立。
4. 每 2 秒 refresh 仍只更新成員名單，不重建路線圖。
5. 手機版 tripMiniMap 固定至少 220px 高度。
6. 原有 OSM/CARTO、MQTT、即時定位、聊天室、路線預覽等功能全部保留。

啟動：
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
