

import datetime
import pykakasi

class reaction:
    def __init__(self):
        self.infos = None
        self.names = None
        self.score = 0
        self.kakasi = pykakasi.kakasi()
        self.kakasi.setMode('K', 'H')
        self.kakasi.setMode('J', 'H')
        self.conversion = self.kakasi.getConverter()
        # self.last_deal_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.last_deal_time = '2024-10-18 15:34:12'
        self.last_deal_time = datetime.datetime.strptime(self.last_deal_time, '%Y-%m-%d %H:%M:%S')
        self.question_list = ['おもいますか', 'かんがえますか', 'どうですか']

    def send(self, infos, names):
        self.infos = infos
        self.names = names

    def check(self):
        dealed_flag = False
        temp_time = self.last_deal_time
        teacher_info = self.infos[0]
        teacher_time_stump = None
        for time_stump, text in teacher_info[::-1]:
            for name in self.names[1:]:
                for question in self.question_list:
                    text = self.conversion.do(text)
                    if name in text and question in text:
                        teacher_time_stump = datetime.datetime.strptime(time_stump, '%Y-%m-%d %H:%M:%S')
                        target_student_name = name
        if teacher_time_stump:
            student_name_index = self.names.index(target_student_name)
            student_info = self.infos[student_name_index]
            for time_stump, text in student_info[::-1]:
                student_time_stump = datetime.datetime.strptime(time_stump, '%Y-%m-%d %H:%M:%S')
                # 受講生の発言した時間が過去に処理した最も遅い時間の発言よりも後なら
                if self.last_deal_time < student_time_stump:
                    # 最も遅い時間を記録しておく
                    if temp_time < student_time_stump:
                        temp_time = student_time_stump
                    if student_time_stump >= teacher_time_stump:
                        if 'はい' in ''.join(list(text)[:5]):
                            self.score += 100
                            dealed_flag = True
                        else:
                            self.score -= 100
                            dealed_flag = False
        # 処理した最も遅い時間を更新
        self.last_deal_time = temp_time
        print(f'今の返事スコア：{self.score}')
        print(self.last_deal_time)
        return dealed_flag


if __name__ == '__main__':
    reaction_check = reaction()
    reaction_check.send(infos=[[['2024-10-18 16:45:58', 'それでは'], ['2024-10-18 16:46:05', 'どう思いますか？山田さん']],
                               [['2024-10-18 16:46:06', 'えっとー、それはダメだと思います']]],
                        names=['こうし', 'やまだ'])
    reaction_check.check()
    reaction_check.send(infos=[[['2024-10-18 16:45:58', 'それでは'], ['2024-10-18 16:46:05', 'どう思いますか？山田さん']],
                               [['2024-10-18 16:46:06', 'えっとー、それはダメだと思います'], ['2024-10-18 16:46:07', 'はい、えっとー、それはダメだと思います']]],
                        names=['こうし', 'やまだ'])
    reaction_check.check()
    reaction_check.send(infos=[[['2024-10-18 16:45:58', 'それでは'], ['2024-10-18 16:46:05', '山田さんが言っていた通り進めます。']],
                               [['2024-10-18 16:46:08', 'えっとー、それはダメだと思います']]],
                        names=['こうし', 'やまだ'])
    reaction_check.check()