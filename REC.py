from vosk import KaldiRecognizer
import sounddevice as sd
import json
import string
import queue
import threading
import datetime
from VoiceToneCheck import Voicetone


class VTT:

    def __init__(self):
        self.Q = queue.Queue()
        self.SAMPLE_RATE = 8000
        self.BUFFER_DURATION = 5
        self.audio_device = sd.default.device[0]
        self.device_info = sd.query_devices(self.audio_device, "input")
        self.samplerate = int(self.device_info["default_samplerate"])
        self.results = []
        self.pitch_name = None
        self.pitch_score = 0
        self.last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stop_event = threading.Event()
        self.voice_tone_check = Voicetone.voicetone()

    # ボイスをキューに追加し、音階判定を行う
    def callback(self, indata, frames, time, status):
        self.Q.put(bytes(indata))


    # 音声取り込み&音声をテキストに変換
    def voice_to_text(self, model):
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = self.SAMPLE_RATE*self.BUFFER_DURATION, device=self.audio_device,
                dtype="int16", channels=1, callback=self.callback):
            print("#" * 80)
            print(f"recording {id(model)}")
            print("#" * 80)
            rec = KaldiRecognizer(model, self.samplerate)
            # メインスレッドからストップ命令が出るまで
            while not self.stop_event.is_set():
                data = self.Q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    result = json.loads(result)
                    result = result['text']
                    result = result.replace(' ', '')
                    if result in string.whitespace:
                        continue
                    else:
                        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.last_update = now
                        self.pitch_name, self.pitch_score = self.voice_tone_check.what_is_doremi(data)
                        self.results.append([now, result])
                        print(f'success record! time : {now}')
            # ループ脱出確認
            print('Task Kill "voice_to_text()"')

    # 音声認識スレッドの停止
    def stop(self):
        self.stop_event.set()