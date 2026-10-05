共乘 Go - Cloudflare Quick Tunnel 測試說明

最簡單方式
==========
直接雙擊：

    start_windows_cloudflare.bat

它會：
1. 檢查 Python。
2. 檢查 cloudflared。
3. 若 cloudflared 沒裝，可自動用 winget 安裝。
4. pip install requirements.txt。
5. python manage.py migrate。
6. 開新視窗啟動 Django 0.0.0.0:8000。
7. 在目前視窗啟動 Cloudflare Quick Tunnel。

成功後會看到類似：

    https://abc-def-123.trycloudflare.com

把這個 HTTPS 網址貼到 iPhone Safari / LINE 內建瀏覽器測試。


如果 Django 已經在跑
===================
雙擊：

    start_cloudflare_only.bat


重要
====
- Quick Tunnel 不需要 Cloudflare 帳號或網域。
- Quick Tunnel 適合開發/測試，不是正式部署。
- 網址通常每次重新啟動都不同。
- 關閉 cloudflared 視窗，公開網址就失效。
- 因為是 HTTPS，在 iPhone 上測 Geolocation 比 http://192.168.x.x:8000 合適。
