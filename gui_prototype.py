import tkinter as tk
import random

class FriendlyBadCopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("友善黑臉 (Friendly Bad Cop) - 噪音模擬器")
        self.root.geometry("450x300")
        self.root.configure(padx=20, pady=20)

        # 1. 準備『友善提醒語句庫』
        self.messages = [
            "哈囉～現在的音量好像有點大喔！可以稍微降低一點點嗎？感謝啦！🙌",
            "嗨嗨，不知道是不是錯覺，聲音好像傳到我這了。麻煩留意一下音量唷～🎵",
            "親愛的室友，目前音量微超標，為了美好的居住品質，麻煩小聲一點點唷！✨",
            "不好意思打擾了，現在的聲音有點影響到我囉，拜託再小聲一點點，謝謝！🙏",
            "音量計顯示現在有點熱鬧喔！需要安靜一下下～🤫 感謝配合！"
        ]

        # 介面排版 - 標題
        self.title_label = tk.Label(
            root, 
            text="室友噪音模擬測試", 
            font=("Microsoft JhengHei", 16, "bold")
        )
        self.title_label.pack(pady=(0, 15))

        # 介面排版 - 訊息顯示區 (用來顯示抽中的友善提醒)
        self.message_label = tk.Label(
            root, 
            text="目前環境很安靜 😌\n(尚未偵測到噪音)", 
            font=("Microsoft JhengHei", 12),
            fg="green",         # 預設為綠色表示安全
            wraplength=400,     # 若句子太長會自動換行
            justify="center",
            height=4
        )
        self.message_label.pack(pady=10)

        # 2. 建立『模擬按鈕』
        self.noise_button = tk.Button(
            root, 
            text="🚨 模擬按鈕：偵測到噪音過大！", 
            font=("Microsoft JhengHei", 12),
            bg="#ffcccc",                # 淺紅色背景
            activebackground="#ff9999",  # 按下時的顏色
            command=self.trigger_noise_alert # 按下時執行的功能
        )
        self.noise_button.pack(pady=20, ipadx=10, ipady=5)

    # 3. 按下按鈕後執行的邏輯
    def trigger_noise_alert(self):
        """當按下按鈕時觸發的邏輯"""
        
        # a. 隨機從語句庫中選出一句話
        selected_message = random.choice(self.messages)
        
        # b. 更新螢幕上的文字與顏色
        self.message_label.config(
            text=f"【系統發送提醒給室友】\n\n「{selected_message}」",
            fg="#d9534f"  # 將文字變成紅色，代表警示
        )

if __name__ == "__main__":
    # 啟動 Tkinter 視窗應用程式
    root = tk.Tk()
    app = FriendlyBadCopApp(root)
    root.mainloop()
