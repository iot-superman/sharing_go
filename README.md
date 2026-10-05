共乘 Go Django - iPhone / LINE 內建瀏覽器 精確選點修正版

主要修正
1. iPhone Safari / LINE 內建瀏覽器點「精確選」時，地圖 Modal 改成手機全螢幕。
2. 使用 100dvh / 100svh，避免 iOS 動態網址列造成 Modal 高度為 0 或地圖被裁切。
3. Bootstrap shown.bs.modal 若沒有觸發，350ms 後仍會強制初始化 Leaflet。
4. Bootstrap CDN / Modal 若失敗，加入純 DOM fallback，仍可彈出精確選點畫面。
5. Leaflet 在 iOS WebView 會做多次 invalidateSize，避免白畫面/只有一角地圖。
6. 加入明確「關閉」按鈕。
7. 使用 http://192.168.x.x 時，iPhone 可能禁止 Geolocation；但仍可手動點地圖精確選位置。
8. 原有地址搜尋、OSM/CARTO、MQTT、即時定位、聊天室、路線預覽功能全部保留。

測試網址
- Windows 本機：http://127.0.0.1:8000
- iPhone 區網：http://你的電腦IP:8000

注意
iPhone 的「目前位置」功能最好使用 HTTPS。
純 HTTP 區網網址時，地圖點選可用，但 Geolocation 可能被瀏覽器安全機制封鎖。

啟動
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
