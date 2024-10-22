
import numpy as np

class voicetone:

    def __init__(self):
        self.pitch_name = None
        self.index = None

    # 周波数からドレミの音階名に変換する関数
    def frequency_to_doremi(self, frequency):
        A4 = 440.0  # 標準ピッチ A4 (ラ) の周波数
        if frequency <= 0:
            return None

        # 音階を半音単位で計算
        semitones = 12 * np.log2(frequency / A4)
        pitch_index = int(np.round(semitones)) + 69  # MIDIのノート番号

        # ドレミに対応する音名のマッピング
        doremi_names = ['ド', 'ド#', 'レ', 'レ#', 'ミ', 'ファ', 'ファ#', 'ソ', 'ソ#', 'ラ', 'ラ#', 'シ']
        pitch_name = doremi_names[pitch_index % 12]
        index = doremi_names.index(pitch_name)
        octave = pitch_index // 12 - 1  # オクターブの計算
        return pitch_name, index

    # ドレミ調査
    def what_is_doremi(self, indata, samplerate):
        # 音声信号をnumpy配列に変換
        audio_data = np.frombuffer(indata, dtype=np.int16)
        
        # FFTを使って音声の周波数成分を取得
        fft_result = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1 / samplerate)
        
        # 最大の振幅を持つ周波数を見つける
        dominant_freq = freqs[np.argmax(np.abs(fft_result))]
        
        # 周波数からドレミ音階に変換
        pitch_name, index = self.frequency_to_doremi(dominant_freq)
        if pitch_name:
            score = 100 - (abs(index-7) * 15)
            self.pitch_name = pitch_name
            self.score = score

    # 声のトーン, スコアを取得して返す
    def get_result_info(self):
        return self.pitch_name, self.score