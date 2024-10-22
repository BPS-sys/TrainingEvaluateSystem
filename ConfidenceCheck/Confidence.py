
import datetime
import pykakasi


class confidence:

    def __init__(self):
        self.kakasi = pykakasi.kakasi()
        self.kakasi.setMode('K', 'H')
        self.kakasi.setMode('J', 'H')
        self.conversion = self.kakasi.getConverter()
        self.score = 0
        self.student_infos = None
        self.infos = None
        # self.last_deal_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.last_deal_time = '2024-10-18 15:34:12'
        self.last_deal_time = datetime.datetime.strptime(self.last_deal_time, '%Y-%m-%d %H:%M:%S')
        self.out_list = ['おもいます']

    def send(self, infos):
        self.infos = infos

    def check(self):
        dealed_flag = False
        temp_time = self.last_deal_time
        self.student_infos = self.infos[1:]
        for student_info in self.student_infos:  # 受講生個人のデータ
            for time_stump, text in student_info:
                student_time_stump = datetime.datetime.strptime(time_stump, '%Y-%m-%d %H:%M:%S')
                # 受講生の発言した時間が過去に処理した最も遅い時間の発言よりも後なら
                if self.last_deal_time < student_time_stump:
                    # 最も遅い時間を記録しておく
                    if temp_time < student_time_stump:
                        temp_time = student_time_stump
                    hira_text = self.conversion.do(text)
                    for out_text in self.out_list:
                        if out_text in hira_text:
                            self.score -= 100
                            dealed_flag = True
                        else:
                            self.score += 100
                            dealed_flag = True
        # 処理した最も遅い時間を更新
        self.last_deal_time = temp_time
        print(self.score)
        print(self.last_deal_time)
        return dealed_flag

if __name__ == '__main__':
    confidence_check = confidence()
    confidence_check.send([[['2024-10-18 16:45:58', 'それでは'], ['2024-10-18 16:46:05', 'どう思いますか？山田さん']],
                     [['2024-10-18 16:46:06', 'えっとー、それはダメだと思います']]])
    confidence_check.check()
    confidence_check.send([[['2024-10-18 16:45:58', 'それでは'], ['2024-10-18 16:46:05', 'どう思いますか？山田さん']],
                     [['2024-10-18 16:46:06', 'えっとー、それはダメだと思います'], ['2024-10-18 16:46:07', 'あ、間違えた。えっとー、それはダメです']]])
    confidence_check.check()