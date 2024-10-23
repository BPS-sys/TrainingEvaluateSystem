
import tkinter as tk
from back_process import BackProcess
import threading
import re
from tkinter import messagebox
from tkinter.ttk import *
import sounddevice as sd
from tkinterdnd2 import *


# マイクに該当するデバイスIDを自動取得する関数
def get_microphone_devices():
    devices = sd.query_devices()
    mic_ids = []
    for idx, device in enumerate(devices):
        # デバイスの名前や最大入力チャネルをチェックしてマイクデバイスかを判断
        if device['max_input_channels'] > 0:  # 入力チャネルが1以上あるものはマイクと仮定
            mic_ids.append(idx)
    return mic_ids

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
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        self.user_names = ['こうし', 'ゆうき']
        self.reaction_question_list = ['おもいますか', 'かんがえますか', 'どうですか']
        self.confidence_out_list = ['おもいます']
        self.mic_num = len(self.user_names)
        self.backprocess = None
        self.press_enter_key_num = 0
        self.now_tab_name = None
        self.mic_ids = []
        self.create_widget()

    def create_widget(self):
        self.canvas = tk.Canvas(width=self.root_width, height=self.root_height, bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.entry_box = tk.Entry(self.root)
        self.entry_box.place(x=10, y=150, height=25)
        self.add_button = tk.Button(self.root, height=1, text='開始', command=self.press_start_button)
        self.add_button.place(x=140, y=150)
        self.write_mic_queue_button = tk.Button(self.root, width=18, height=1, text='マイクの書き出し', command=self.press_write_mic_queue)
        self.write_mic_queue_button.place(x=180, y=40)
        self.drop_canvas = tk.Canvas(width=135, height=105, bg='red', highlightthickness=0)
        self.drop_canvas.place(x=180, y=70)
        self.drop_canvas.drop_target_register(DND_FILES)
        self.tab = Notebook(self.root, width=160, height=110)
        self.tab.place(x=10, y=10)
        self.tab1 = tk.Frame(self.tab)
        self.tab2 = tk.Frame(self.tab)
        self.tab3 = tk.Frame(self.tab)
        # タブ1
        self.tab.add(self.tab1, text='名前')
        scroll_name = tk.Scrollbar(self.tab1)
        self.list_value_name = tk.StringVar()
        self.list_value_name.set(self.user_names)
        self.listbox_name = tk.Listbox(self.tab1, height=6, width=22, listvariable=self.list_value_name, selectmode="single", yscrollcommand=scroll_name.set)
        scroll_name.place(x=140, y=10, height=90)
        self.listbox_name.place(x=5, y=10)
        # タブ2
        self.tab.add(self.tab2, text='返事')
        scroll_reaction = tk.Scrollbar(self.tab2)
        self.list_value_reaction = tk.StringVar()
        self.list_value_reaction.set(self.reaction_question_list)
        self.listbox_reaction = tk.Listbox(self.tab2, height=6, width=22, listvariable=self.list_value_reaction, selectmode="single", yscrollcommand=scroll_reaction.set)
        scroll_reaction.place(x=140, y=10, height=90)
        self.listbox_reaction.place(x=5, y=10)
        # タブ3
        self.tab.add(self.tab3, text='自信')
        scroll_confidence = tk.Scrollbar(self.tab3)
        self.list_value_confidence = tk.StringVar()
        self.list_value_confidence.set(self.confidence_out_list)
        self.listbox_confidence = tk.Listbox(self.tab3, height=6, width=22, listvariable=self.list_value_confidence, selectmode="single", yscrollcommand=scroll_confidence.set)
        scroll_confidence.place(x=140, y=10, height=90)
        self.listbox_confidence.place(x=5, y=10)
        
        self.setting_bind()
    
    def press_write_mic_queue(self):
        ids = get_microphone_devices()
        with open('mics.txt', 'w') as f:
            pass
        with open('mics.txt', 'a') as f:
            for id in ids:
                f.write(str(id)+'\n'+str(sd.query_devices()[id])+'\n')

    def press_start_button(self):
        self.canvas.delete('error')
        if self.mic_ids:
            ret = messagebox.askokcancel('最終確認', '評価システムを起動しますか？')
            if ret:
                self.main()
                messagebox.showinfo('メッセージ', 'システムを起動しました')
            else:
                messagebox.showwarning('メッセージ', 'システムの起動を中止しました')
        else:
            self.canvas.create_text(248, 24, text='マイクの書き出しが必要', fill='red', tag='error', font=('MS明朝', 10))


    def press_Deletekey(self):
        if self.now_tab_name == '名前':
            selected_index = self.listbox_name.curselection()[0]
            if selected_index != 0:
                del self.user_names[selected_index]
                self.list_value_name.set(self.user_names)
        elif self.now_tab_name == '返事':
            selected_index = self.listbox_reaction.curselection()[0]
            del self.reaction_question_list[selected_index]
            self.list_value_reaction.set(self.reaction_question_list)
        elif self.now_tab_name == '自信':
            selected_index = self.listbox_confidence.curselection()[0]
            del self.confidence_out_list[selected_index]
            self.list_value_confidence.set(self.confidence_out_list)
        
    def press_Enterkey(self):
        self.canvas.delete('error')
        self.press_enter_key_num += 1
        if self.press_enter_key_num > 1:
            self.press_enter_key_num = 0
            text = self.entry_box.get()
            self.entry_box.delete(0, tk.END)
            if not re.search('[^\u3040-\u309F]', text):
                if self.now_tab_name == '名前':
                    self.user_names.append(text)
                    self.list_value_name.set(self.user_names)
                elif self.now_tab_name == '返事':
                    self.reaction_question_list.append(text)
                    self.list_value_reaction.set(self.reaction_question_list)
                elif self.now_tab_name == '自信':
                    self.confidence_out_list.append(text)
                    self.list_value_confidence.set(self.confidence_out_list)
            else:
                self.canvas.create_text(248, 24, text='ひらがなのみ対応です', fill='red', tag='error', font=('MS明朝', 10))
                
    def keyrelease_event_entrybox(self, e):
        self.canvas.delete('error')
        if e.keysym == 'Return':
            self.press_Enterkey()
        else:
            self.press_enter_key_num = 0

    def keyrelease_event_listbox(self, e):
        if e.keysym == 'Delete':
            self.press_Deletekey()

    def tab_changed(self, e):
        select_tab = e.widget
        self.now_tab_name = select_tab.tab(select_tab.select(), 'text')
        
    def setting_bind(self):
        self.entry_box.bind('<KeyRelease>', self.keyrelease_event_entrybox)
        self.listbox_name.bind('<KeyRelease>', self.keyrelease_event_listbox)
        self.listbox_reaction.bind('<KeyRelease>', self.keyrelease_event_listbox)
        self.listbox_confidence.bind('<KeyRelease>', self.keyrelease_event_listbox)
        self.tab.bind('<<NotebookTabChanged>>', self.tab_changed)
        self.drop_canvas.dnd_bind('<<Drop>>', self.mic_text_read)

    def mic_text_read(self, e):
        path = e.data
        if path.endswith('.txt'):
            with open(path) as f:
                mic_ids = f.read()
            self.mic_ids = list(map(int, mic_ids.split('\n')))
            print(self.mic_ids)


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
        self.backprocess = BackProcess(mic_ids=self.mic_ids, user_names=self.user_names, reaction_question_list=self.reaction_question_list, confidence_out_list=self.confidence_out_list)
        voice_recognition_thread = threading.Thread(target=self.backprocess.start_voice_recognition)
        voice_recognition_thread.start()
        self.voice_update_check_process_thread = threading.Thread(target=self.backprocess.voice_update_check_process)
        self.voice_update_check_process_thread.start()


# 根幹
def UI_main():
    ROOT = TkinterDnD.Tk()
    App(ROOT)
    ROOT.mainloop()


# 誤爆防止
if __name__ == '__main__':
    UI_main()
