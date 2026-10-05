你截圖裡的錯誤原因：
舊版 BAT 使用了 UTF-8 中文文字，但 Windows CMD 以傳統碼頁解析，
所以 @echo off 被讀成亂碼，才會出現「不是內部或外部命令」等錯誤。

這版 BAT 已改成「純 ASCII 英文」：
- 不受 Windows 中文 Big5 / UTF-8 碼頁影響
- 不需要 chcp 65001
- 不會再把 @echo off 解析成亂碼

使用方式：
1. 雙擊 start_windows_cloudflare.bat
2. 等 Django 啟動
3. 等 cloudflared 顯示真正的網址，例如：
   https://abc-def-123.trycloudflare.com
4. 複製「cloudflared 真正顯示的網址」到 iPhone。
5. 不要自己輸入 xx.trycloudflare.com；xx 只是範例文字。

若 cloudflared 已裝好、Django 也已經在跑：
可直接雙擊 start_cloudflare_only.bat。
