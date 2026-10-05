共乘 Go - 行程路線圖不抖動修正版

問題原因
========
原本 refresh() 每 2 秒會呼叫 loadTrip()。
loadTrip() 每次都：
1. tripMiniMap.remove()
2. tripBox.innerHTML = ...
3. new L.map()
4. 再抓一次路線並 fitBounds()

所以路線小圖會每 2 秒重建，看起來像一直刷新 / 抖動。

本版修正
========
1. 同一筆行程、同一起終點時，Leaflet 小地圖只建立一次。
2. 每 2 秒只更新成員清單和人數，不碰地圖 DOM。
3. 只有行程 ID / 日期時間 / 起點 / 終點真的改變才重建地圖。
4. refresh 加 refreshBusy，避免 API 慢時 setInterval 重入。
5. 行程頁顯示時，不再背景重複 renderHome()/fitBounds()。
6. 移除 refresh() 裡重複的 loadMsgs() 呼叫。
7. MQTT、即時定位、OSM/CARTO、路線預覽等功能都保留。

啟動
====
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
