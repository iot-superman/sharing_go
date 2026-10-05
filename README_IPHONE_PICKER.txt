共乘 Go - iPhone / LINE 手動精確選點強制修正版

這版針對：
http://192.168.x.x:8000
在 iPhone Safari / LINE 內建瀏覽器點「精確選」完全沒有彈出地圖的問題。

修正方式：
1. 精確選視窗不再依賴 Bootstrap Modal 的 shown.bs.modal / transition。
2. 點「精確選」後直接以 position:fixed 全螢幕 overlay 強制顯示。
3. iOS 會在 requestAnimationFrame 後初始化 Leaflet。
4. 120ms / 420ms / 900ms 再做多次 invalidateSize，避免白圖或尺寸為 0。
5. 關閉按鈕也不再依賴 data-bs-dismiss。
6. http://192.168.x.x:8000 即使 GPS 被 iOS 禁止，仍可手動點地圖選集合點/目的地。
7. 若要使用「目前位置 GPS」，仍建議 HTTPS（Cloudflare Tunnel / Render）。

測試：
Windows 啟動：
python manage.py runserver 0.0.0.0:8000

iPhone：
http://你的電腦IP:8000

進入「建立共乘」→ 點「精確選」
應直接全螢幕開地圖，手動點地圖即可選位置。
