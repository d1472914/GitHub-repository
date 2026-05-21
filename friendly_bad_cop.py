import random
from datetime import datetime

class FriendlyBadCop:
    """
    友善黑臉 (Friendly Bad Cop) 核心邏輯
    負責分析室友的行為（如：噪音、未洗碗）並根據情況與時間產生適當的友善提醒訊息。
    """
    def __init__(self):
        # 1. 設定不同時段的噪音閾值 (分貝 dB)
        self.noise_thresholds = {
            "daytime": 65,   # 早上 8 點到晚上 10 點 (白天容忍度較高)
            "nighttime": 45  # 晚上 10 點到早上 8 點 (深夜需要安靜)
        }
        
        # 2. 紀錄各項違規的連續次數，用於「升級」提醒的語氣
        self.violation_counts = {
            "noise": 0,
            "dishes": 0
        }
        
        # 3. 友善但堅定的提醒語錄庫 (依據嚴重程度分級)
        self.messages = {
            "noise": {
                "level_1": [
                    "哈囉～現在的音量好像有點大喔！可以稍微降低一點點嗎？感謝啦！🙌",
                    "嗨嗨，不知道是不是錯覺，聲音好像傳到我這了。麻煩留意一下音量唷～🎵",
                    "親愛的室友，目前音量微超標，為了美好的居住品質，麻煩小聲一點點唷！✨"
                ],
                "level_2": [
                    "不好意思打擾了，現在的聲音有點影響到我囉，拜託再小聲一點點，謝謝！🙏",
                    "音量計顯示現在有點熱鬧喔！需要安靜一下下～🤫 感謝配合！"
                ],
                "level_3": [
                    "⚠️ 溫馨提醒：目前音量已經連續超標囉！為了大家的耳膜與和平，請立刻降低音量，感謝！🥷",
                    "嗨，連續收到噪音警報了 🚨。如果再不大減音量，友善黑臉就要變身囉！"
                ]
            }
        }

    def _get_current_period(self):
        """判斷現在是白天還是深夜"""
        hour = datetime.now().hour
        if 8 <= hour < 22:
            return "daytime"
        return "nighttime"

    def analyze_noise(self, current_decibels: float):
        """
        傳入當前的噪音分貝數，判斷是否需要發送提醒。
        回傳: (是否觸發提醒: bool, 提醒訊息: str)
        """
        period = self._get_current_period()
        limit = self.noise_thresholds[period]
        
        print(f"[系統偵測] 目前時間屬於: {period}，噪音閾值為: {limit}dB，當前偵測到: {current_decibels}dB")
        
        if current_decibels > limit:
            # 噪音超標，增加違規次數
            self.violation_counts["noise"] += 1
            count = self.violation_counts["noise"]
            
            # 根據連續違規次數，決定語氣層級
            if count == 1:
                level = "level_1"
            elif count == 2:
                level = "level_2"
            else:
                level = "level_3"
                
            # 隨機挑選該層級的一句話
            msg = random.choice(self.messages["noise"][level])
            
            self._send_notification(msg)
            return True, msg
            
        else:
            # 如果安靜下來（低於標準），則歸零違規次數
            # 這樣下次吵鬧時，又會從最友善的 level 1 開始
            if self.violation_counts["noise"] > 0:
                print("👍 噪音已經恢復正常標準，計數器歸零。")
            self.violation_counts["noise"] = 0
            
            return False, "目前音量正常，世界和平。"

    def _send_notification(self, message: str):
        """
        將訊息推播出去的接口（未來可串接 Line Notify, Slack Bot 等）
        """
        print(f"💬 [發送推播] : {message}")


# ==========================================
# 測試與模擬情境
# ==========================================
if __name__ == "__main__":
    bot = FriendlyBadCop()
    
    print("--- 🟢 測試情境 1：正常音量 ---")
    bot.analyze_noise(40)
    
    print("\n--- 🟡 測試情境 2：第一次噪音超標 ---")
    # 假設目前是深夜 (閾值 45dB)，但偵測到 50dB
    # 這裡我們為了測試，直接塞入一個高於兩者閾值的數值，如 70dB
    bot.analyze_noise(70) 
    
    print("\n--- 🟠 測試情境 3：第二次連續噪音超標 ---")
    bot.analyze_noise(72)
    
    print("\n--- 🔴 測試情境 4：第三次連續噪音超標（語氣升級） ---")
    bot.analyze_noise(68)
    
    print("\n--- 🟢 測試情境 5：終於安靜下來了 ---")
    bot.analyze_noise(30)
