
from REC import VTT
import threading
from vosk import Model
import copy
from ReactionCheck import Reaction
from ConfidenceCheck import Confidence
from time import sleep
import numpy as np
from PostureCheck import JudgePosture


class BackProcess:

    def __init__(self, mic_ids, user_names, reaction_question_list, confidence_out_list):
        self.mic_num = len(mic_ids)
        self.vtts = [VTT(mic_id) for mic_id in mic_ids]
        self.voice_threads = []
        self.model_path = "vosk-model-ja-0.22"  # 音声認識モデル
        self.model = Model(self.model_path)
        self.before_update = []
        self.user_names = user_names
        self.first_process = True
        self.before_update = None
        self.reaction_question_list = reaction_question_list
        self.confidence_out_list = confidence_out_list
        self.reaction_dealed_flag = None
        self.confidence_dealed_flag = None
        self.voice_result = None
        self.reaction = Reaction.reaction(score_list=list(map(int, np.zeros((len(self.user_names),)))), question_list=self.reaction_question_list)
        self.confidence = Confidence.confidence(score_list=list(map(int, np.zeros((len(self.user_names),)))), out_list=confidence_out_list)
        self.stop_event = threading.Event()

    # 音声認識を別スレッドで開始
    def start_voice_recognition(self):
        for vtt in self.vtts:
            thread = threading.Thread(target=vtt.voice_to_text, args=[self.model])
            thread.start()
            self.voice_threads.append(thread)
    
    # 声のアップデートがされているか確認
    def voice_update_check_process(self):
        while not self.stop_event.is_set():
            last_update = self.check_voice_last_update()
            if self.first_process:
                self.first_process = False
                self.before_update = copy.deepcopy(last_update)
            if self.before_update != last_update:
                self.voice_result = self.get_voice_to_text_results()
                self.reaction_check()
                self.confidence_check()
                self.before_update = copy.deepcopy(last_update)
            sleep(0.5)

    def start_posture_check(self):
        for id, user_name in enumerate(self.user_names):
            JudgePosture()
        for id, user_name in enumerate(self.user_names):
            thread = threading.Thread(target=JudgePosture.taking, args=[user_name, id])
            thread.start()

    # リアクションチェック
    def reaction_check(self):
        self.reaction.send(infos=self.voice_result, names=self.user_names)
        self.reaction_dealed_flag = self.reaction.check()

    # やる気チェック
    def confidence_check(self):
        self.confidence.send(infos=self.voice_result)
        self.confidence_dealed_flag = self.confidence.check()

    # 話者それぞれの声が収録された最後の時間を取得
    def check_voice_last_update(self):
        return [vtt.last_update for vtt in self.vtts]
    
    # 声->テキストに変換後のテキストを取得
    def get_voice_to_text_results(self):
        return [vtt.results for vtt in self.vtts]
    
    # 声のトーンの音程？音階？を取得（ドレミ）
    def get_voice_tone_results(self):
        return [vtt.pitch_name for vtt in self.vtts]
    
    # 声のトーンのスコアを取得
    def get_voice_tone_score(self):
        return [vtt.pitch_score for vtt in self.vtts]
    
    # 指名時の返事スコアを取得
    def get_reaction_score(self):
        return self.reaction.score_list
    
    # 発言への自信スコアを取得
    def get_confidence_score(self):
        return self.confidence.score_list
    
    # 声の収録がされたかを確認しているスレッドをkill
    def stop_voice_update_check(self):
        self.stop_event.set()
        print(f'Task Kill "voice_update_check_process()"')

    # 声の収録スレッドをすべてkill
    def stop_voice_recognition(self):
        for i, vtt in enumerate(self.vtts): 
            vtt.stop()
            self.voice_threads[i].join()

    def stop_posture(self):

