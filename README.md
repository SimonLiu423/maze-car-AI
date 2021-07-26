---
Title: Maze Car
version: 3.0.4
---
# Maze Car
想要訓練屬於自己的迷宮自走車嗎？

想要跟朋友來場刺激的競賽嗎？

帶上你的自走車往終點衝刺吧！

* 遊戲版本：`3.0.4`

![](https://i.imgur.com/ymZZMyO.png)

# 更新內容
- 配合MLGame系統改動(9.0.8-beta)
- 修改迷宮地圖資料格式為JSON檔
- 修改sensor偵測時的Bug
- 增加車子與終點的絕對座標(回傳給玩家)
- 增加超聲波感測器的數量(可選擇3或5個)

# 遊戲玩法

此遊戲為迷宮自走車模擬遊戲，遊戲過程中玩家控制一台配備有前、中、後三個超聲波感測器的車子，並運用正確的邏輯，讓車子可以最快的走出迷宮。

## 遊戲規則

遊戲最多可以六個人同時進行，目前有迷宮模式和移動迷宮模式。

🚗迷宮模式：玩家可以選擇不同的地圖，目標為抵達迷宮終點，遊戲將記錄不同玩家完成迷宮所花費的時間，並根據速度快慢給出排名與積分。
🚧移動迷宮模式：相較於單純的迷宮，此模式中的地圖配有動態的牆壁，提高迷宮難度。與迷宮模式相同，將根據不同玩家的速度提供排名。

## 遊戲細節

### 物件的單位
遊戲中的單位為公分(cm)，此亦為超聲波感測器回傳值的單位。

### 關於車子
![](https://i.imgur.com/srSifjm.png)
* 10 \* 10 公分大小的正方形車體。
* 玩家透過回左右輪的馬力控制車子的方向與速度。
* 馬達轉速範圍-255(逆轉)~255(正轉)，輸出為0時則靜止。
* 若回傳值超過馬力範圍則是為正轉或逆轉之最大值，例如：回傳左輪馬力300、右輪馬力-400，則實際轉速等同於左輪255、右輪-255。

### 關於迷宮格

* 25 \* 25 公分的正方形，牆壁厚度為5cm。
