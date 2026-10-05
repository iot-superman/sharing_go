共乘 Go - 訊息 Tab 未讀泡泡只計目前加入群組修正版

Bug 原因
========
舊 MQTT client 在切換行程後，可能還有已排進事件佇列的 message callback。
原本 callback 只檢查全域 active / mqttRideId，沒有檢查「訊息 topic 的 rideId」。
因此舊群組或其他群組的訊息可能被 renderChatMessage() 當成即時訊息，
進而讓訊息 Tab 的紅色未讀數增加。

修正
====
1. 未讀數綁定 unreadRideId，只屬於目前 active 共乘。
2. MQTT message topic 必須精確符合：
   carpool-go/v1/ride/<目前 ride id>/chat
3. payload 的 rideId 若存在，也必須等於目前 ride id。
4. senderId 必須存在於目前 active.members。
5. 每次建立 MQTT 連線都帶 generation token；舊 client callback 立即失效。
6. disconnect 時 removeAllListeners() 後再 end(true)。
7. 切換到另一筆行程時，舊群組未讀數自動歸零。
8. 沒有加入任何行程時，未讀 badge 強制隱藏。
9. 既有 MQTT 即時聊天、LINE 泡泡、地圖不抖動等功能保留。

測試
====
A 加入 Ride #1
B 加入 Ride #1
C 在其他 Ride #2 發訊息
=> A/B 的訊息 Tab 未讀數不應增加。

Ride #1 內另一位成員發訊息
=> 未開聊天頁時，未讀數 +1。
=> 打開聊天頁後歸零。
