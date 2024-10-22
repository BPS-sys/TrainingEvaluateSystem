
from REC import VTT
import threading
from vosk import Model
import copy
from ReactionCheck import Reaction
from ConfidenceCheck import Confidence
from time import sleep


class BackProcess:

    def __init__(self, mic_num):
        self.mic_num = mic_num
        self.vtts = [VTT() for _ in range(self.mic_num)]
        self.voice_threads = []
        self.model_path = "vosk-model-ja-0.22"  # 音声認識モデル
        self.model = Model(self.model_path)
        self.before_update = []
        self.first_process = True
        self.before_update = None
        self.reaction_dealed_flag = None
        self.confidence_dealed_flag = None
        self.voice_result = None
        self.user_names = ['こうし', 'やまだ']
        self.reaction = Reaction.reaction()
        self.confidence = Confidence.confidence()
        self.stop_event = threading.Event()

    # 音声認識を別スレッドで開始
    def start_voice_recognition(self):
        for vtt in self.vtts:
            thread = threading.Thread(target=vtt.voice_to_text, args=[self.model])
            thread.start()
            self.voice_threads.append(thread)
    
    def voice_update_check_process(self):
        while not self.stop_event.is_set():
            last_update = self.check_voice_last_update()
            if self.first_process:
                self.first_process = False
                self.before_update = copy.deepcopy(last_update)
            if self.before_update != last_update:
                self.voice_result = self.get_voice_results()
                print(self.get_voice_results())
                self.reaction_check()
                self.before_update = copy.deepcopy(last_update)
            sleep(0.5)

    # リアクション
    def reaction_check(self):
        self.reaction.send(infos=self.voice_result, names=self.user_names)
        self.reaction_dealed_flag = self.reaction.check()

    # やる気
    def confidence_check(self):
        self.confidence.send(infos=self.voice_result)
        self.confidence_dealed_flag = self.confidence.check()

    def check_voice_last_update(self):
        return [vtt.last_update for vtt in self.vtts]
    
    def get_voice_results(self):
        return [vtt.results for vtt in self.vtts]
    
    def get_voice_tone_results(self):
        return [vtt.pitch for vtt in self.vtts]
    
    def stop_voice_update_check(self):
        self.stop_event.set()
        print(f'Task Kill "voice_update_check_process()"')

    def stop_voice_recognition(self):
        for i, vtt in enumerate(self.vtts): 
            vtt.stop()
            self.voice_threads[i].join()
