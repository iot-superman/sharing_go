共乘 Go Django - Render 多裝置「看不到共乘」修正版

診斷
====
這次不是 PostgreSQL 資料沒有共用。

A 手機已建立 Ride #1，A 的畫面可看到。
B 手機截圖是在「行程」Tab。
「行程」使用 /api/my-trip/，這支 API 的定義是：
只回傳「目前這個 client_id 已經建立或加入的共乘」。

因此 B 尚未加入 A 的 Ride #1 時：
GET /api/my-trip/ -> 200, ride=null
是正確行為。

可加入的所有募集是另一支：
GET /api/rides/
前端只有進入「找共乘」時才會呼叫。

從使用者提供的 Render log 可看到大量：
GET /api/my-trip/
但沒有看到 B 當下進入找共乘所需的 GET /api/rides/
因此 B 不是資料庫看不到，而是停在「我的行程」畫面。

本版修正
========
1. B 若沒有 active ride，點「行程」會自動導向「找共乘」。
2. 「首頁沒有行程」增加「查看可加入共乘」按鈕。
3. 「我的行程」空狀態文字改清楚：
   - 我的行程 = 自己已建立/已加入
   - 找共乘 = 所有可加入募集
4. /api/rides/ 後端仍維持回傳所有非 cancelled 募集，不按 client_id 過濾。
5. 不改 PostgreSQL / Render DB 結構，不會破壞既有 Ride 資料。

驗證方式
========
A 手機：
建立 Ride #1。

B 手機：
重新整理 https://carpool-go.onrender.com/
-> 點「找共乘」
或
-> 點「行程」（若尚未加入會自動轉到找共乘）
-> 應看到 A 建立的 Ride #1
-> 按「加入共乘」
-> 之後「行程」才會顯示 Ride #1。
