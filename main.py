
import tkinter as tk
from back_process import BackProcess
import threading
import re
from tkinter import messagebox


# アプリケーションクラス
class App(tk.Frame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root_width = 320
        self.root_height = 185
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root_x = (self.screen_width//2) - (self.root_width//2)
        self.root_y = (self.screen_height//2) - (self.root_height//2)
        self.root.geometry(f'{self.root_width}x{self.root_height}+{self.root_x}+{self.root_y}')
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        self.user_names = ['こうし', 'やまだ']
        self.mic_num = len(self.user_names)
        self.backprocess = None
        self.press_enter_key_num = 0
        self.create_widget()
        # self.main()

    def create_widget(self):
        self.canvas = tk.Canvas(width=self.root_width, height=self.root_height, bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.entry_box = tk.Entry()
        #スクロールバーの作成
        scroll = tk.Scrollbar(self.root)
        #スクロールバーの配置を決める
        self.list_value = tk.StringVar()
        self.list_value.set(self.user_names)
        self.listbox = tk.Listbox(self.root, height=8, width=23, listvariable=self.list_value, selectmode="single", yscrollcommand=scroll.set)
        self.add_button = tk.Button(height=1, text='開始', command=self.press_start_button)
        self.add_button.place(x=140, y=150)
        scroll.place(x=155, y=10, height=132)
        self.listbox.place(x=10, y=10)
        self.entry_box.place(x=10, y=150, height=25)
        self.setting_bind()

    def press_start_button(self):
        ret = messagebox.askokcancel('最終確認', '評価システムを起動しますか？')
        if ret:
            self.main()
            messagebox.showinfo('メッセージ', 'システムを起動しました')
        else:
            messagebox.showwarning('メッセージ', 'システムの起動を中止しました')


    def press_Deletekey(self):
        selected_index = self.listbox.curselection()[0]
        if selected_index != 0:
            del self.user_names[selected_index]
            self.list_value.set(self.user_names)
        
    def press_Enterkey(self):
        self.press_enter_key_num += 1
        if self.press_enter_key_num > 1:
            self.press_enter_key_num = 0
            name = self.entry_box.get()
            self.entry_box.delete(0, tk.END)
            if re.search('[\u3040-\u309F]', name):
                self.user_names.append(name)
                print(self.user_names)
                self.list_value.set(self.user_names)

    def keyrelease_event_entrybox(self, e):
        print(e.keysym)
        if e.keysym == 'Return':
            self.press_Enterkey()
        else:
            self.press_enter_key_num = 0

    def keyrelease_event_listbox(self, e):
        if e.keysym == 'Delete':
            self.press_Deletekey()

    def setting_bind(self):
        self.entry_box.bind('<KeyRelease>', self.keyrelease_event_entrybox)
        self.listbox.bind('<KeyRelease>', self.keyrelease_event_listbox)
    
    # UIを閉じるイベントが発生したとき
    def destroy_window(self):
        ret = messagebox.askokcancel('最終確認', 'システムを終了しますか？')
        if ret:
            if self.backprocess:
                self.backprocess.stop_voice_recognition()
                self.backprocess.stop_voice_update_check()
                self.voice_update_check_process_thread.join()
            messagebox.showinfo('メッセージ', '評価システムは正常に終了しました。\nこのウィンドウを閉じるとアプリケーションを終了します。')
            self.root.destroy()


    # クラス内メイン
    def main(self):
        print('process start')
        self.backprocess = BackProcess(mic_num=self.mic_num, user_names=self.user_names)
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