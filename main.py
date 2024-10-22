
import tkinter as tk
from back_process import BackProcess
import threading



# アプリケーションクラス
class App(tk.Frame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        self.mic_num = 1
        self.backprocess = BackProcess(mic_num=self.mic_num)
        self.main()
    
    # UIを閉じるイベントが発生したとき
    def destroy_window(self):
        self.backprocess.stop_voice_recognition()
        self.backprocess.stop_voice_update_check()
        self.voice_update_check_process_thread.join()
        self.root.destroy()

    # クラス内メイン
    def main(self):
        print('process start')
        voice_recognition_thread = threading.Thread(target=self.backprocess.start_voice_recognition)
        voice_recognition_thread.start()
        self.voice_update_check_process_thread = threading.Thread(target=self.backprocess.voice_update_check_process)
        self.voice_update_check_process_thread.start()


# 根幹
def UI_main():
    ROOT = tk.Tk()
    App(ROOT)
    ROOT.mainloop()


# 誤爆防止
if __name__ == '__main__':
    UI_main()