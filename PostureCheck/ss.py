import cv2
import mediapipe as mp
import time
import numpy as np
import threading


class Posture:
    
    def __init__(self):
        mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.posture_score_list = []
        self.knee_score_list = []
        self.neck_score_list = []
        self.hand_score_list = []
        self.time_stump_list = []
        self.stop_event = threading.Event()
        # 特定のランドマーク（肩、腰、膝、足首）を表示
        self.landmarks_to_display = [   
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,   # 左肩
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,  # 右肩
            self.mp_pose.PoseLandmark.LEFT_HIP,        # 左腰
            self.mp_pose.PoseLandmark.RIGHT_HIP,       # 右腰
            self.mp_pose.PoseLandmark.LEFT_KNEE,       # 左膝
            self.mp_pose.PoseLandmark.RIGHT_KNEE,      # 右膝
            self.mp_pose.PoseLandmark.LEFT_ANKLE,      # 左足首
            self.mp_pose.PoseLandmark.RIGHT_ANKLE      # 右足首
        ]

    def is_sitting(self, landmarks, image_height, threshold=80):
        # 必要なランドマークを取得
        left_hip_y = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * image_height
        right_hip_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y * image_height
        left_knee_y = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y * image_height
        right_knee_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y * image_height

        # 腰と膝のY座標の差を計算
        left_diff = abs(left_hip_y - left_knee_y)
        right_diff = abs(right_hip_y - right_knee_y)

        # 差が閾値以下の場合は「座っている」と判定
        if left_diff < threshold and right_diff < threshold:
            return True
        return False

    # 姿勢がよいかを判定する関数（肩と腰のX座標の差を使用）
    def posture_scoring(self, landmarks, image_width):
        left_shoulder_x = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image_width
        right_shoulder_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image_width
        left_hip_x = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * image_width
        right_hip_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x * image_width
        # 肩と腰のX座標の差を計算
        diff = abs(left_shoulder_x - left_hip_x)
        if diff < 30:
            return 100
        elif diff < 50:
            return 50
        else:
            return 0

    # ９０度になっているかを判定する関数（左膝と左足首のX座標の差を使用）
    def posture_scoring_knee_ankle(self, landmarks, image_width):
        left_knee_x = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * image_width
        left_ankle_x = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x * image_width
        # 膝と足首のX座標の差を計算
        diff = abs(left_knee_x - left_ankle_x)
        if diff < 30:
            return 100
        elif diff < 50:
            return 50
        else:
            return 0

    #膝と足首の位置
    def bottom_is_good(self, landmarks, image_width, threshold=80):
        #座標取得
        right_knee_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x * image_width
        left_knee_x = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * image_width
        right_ankle_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * image_width
        left_ankle_x = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x * image_width

        #y軸の誤差
        left_diff = abs(left_knee_x - left_ankle_x)
        right_diff = abs(right_knee_x - right_ankle_x)

        if left_diff < threshold and right_diff < threshold:
            return True
        return False

    #首と肩の位置
    def neck_scoring(self, landmarks, image_height, image_width):
        #座標取得
        right_ear_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].x * image_width
        right_shoulder_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image_width
        left_ear_x = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x * image_height
        left_shoulder_x = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image_height

        #y軸の誤差
        left_diff = abs(left_ear_x - left_shoulder_x)
        right_diff = abs(right_ear_x - right_shoulder_x)

        if left_diff < 40 and right_diff <40:
            return 'Perfect'
        elif 40 <= left_diff <= 55 or 40 <= right_diff <= 55:
            return 'Good'
        else:
            return 'Bad'


    #手首と膝のy軸とz軸を検証する
    def hand_scoring(self, landmarks, image_height, image_width):#z軸:膝=手首 y軸:膝-手首<限界値　x軸:閾値<膝-手首<限界値
        #正規化
        right_knee_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x * image_width
        right_knee_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y * image_height
        right_knee_z = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].z * image_height
        right_wrist_x = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x * image_width
        right_wrist_y = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y * image_height
        right_wrist_z = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].z * image_height

        #x軸とy軸の差
        right_x_diff = abs(right_knee_x - right_wrist_x)
        right_y_diff = abs(right_knee_y - right_wrist_y)
        right_z_diff = abs(right_knee_z - right_wrist_z)

        if 30 <= right_x_diff <= 60 and 40 <= right_y_diff <= 80 and 0 <= right_z_diff <= 50:#x30~50, y40~50, z0~10
            return 'Perfect'
        elif ((20 <= right_x_diff <= 29 or 51 <= right_x_diff <= 60) and
                (30 <= right_y_diff <= 39 or 51 <= right_y_diff <= 60) and
                11 <= right_z_diff <= 20):#x20~29・51~60, y30~39,51~60, z11~20 
            return 'Good'
        else:
            return 'Bad'
    # Webカメラ入力の場合：
    def taking(self, user_name, id):
        timemark = 0
        cap = cv2.VideoCapture(id)
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            last_time = time.time()  # 最後に座標を取得した時間を記録
            while cap.isOpened() and not self.stop_event.is_set():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # 画像を水平反転し、BGRからRGBに変換
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image_height, image_width, _ = image.shape

                # 画像にポーズアノテーションを描画
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # 1秒ごとに座標を取得する
                current_time = time.time()
                if current_time - last_time > 1:
                    last_time = current_time  # 現在の時間を記録して次回の基準にする

                    # 特定のランドマークを個別に描画する
                    if results.pose_landmarks:
                        landmark_points = {
                            2: '左目', 5: '右目', 11: '左肩', 12: '右肩', 13: '左肘', 14: '右肘',
                            15: '左手首', 16: '右手首', 23: '左腰', 24: '右腰', 25:'左膝', 26:'右膝',
                            27:'左足首',28: '右足首'
                        }

                        # ランドマークを一つずつ描画し、座標を取得する
                        for landmark_index, label in landmark_points.items():
                            landmark = results.pose_landmarks.landmark[landmark_index]

                            # ランドマークの座標を取得して描画
                            h, w, _ = image.shape
                            cx, cy = int(landmark.x * w), int(landmark.y * h)
                            cz = landmark.z  # z軸の座標  

                            # ランドマークの位置に円を描画
                            cv2.circle(image, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

                            # 座標をコンソールに表示（X, Y, Z）
                            print(f"{label}: X座標: {cx}, Y座標: {cy}, Z座標: {cz:.4f}")

                            # ランドマークに対応するラベルを表示
                            # cv2.putText(image, label, (cx + 10, cy + 10),
                            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        #if bottom_is_good(results.pose_landmarks.landmark, image_width):
                        #   cv2.putText(image, 'good', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        #else:
                        #    cv2.putText(image, 'bad', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                        # 座っているかを判定
                        if is_sitting(results.pose_landmarks.landmark, image_height):
                            cv2.putText(image, 'Sitting', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            # 左膝と左足首のX座標を使って９０度になっているかを判定
                            #knee = posture_scoring_knee_ankle(results.pose_landmarks.landmark, image_width)
                            knee_score_list.append(posture_scoring_knee_ankle(results.pose_landmarks.landmark, image_width))
                            #cv2.putText(image, f'Posture (Knee-Ankle): {knee}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                            # 姿勢が良いかを判定
                            #posture = posture_scoring(results.pose_landmarks.landmark, image_height, image_width)
                            posture_score_list.append(posture_scoring(results.pose_landmarks.landmark, image_width))
                            #cv2.putText(image, f'Posture: {posture}', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                            #首の判定
                            #neck = neck_scoring(results.pose_landmarks.landmark, image_height, image_width)
                            neck_score_list.append(neck_scoring(results.pose_landmarks.landmark, image_height, image_width))
                            #cv2.putText(image, f"neck:{neck}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                            #手首の判定
                            #hand = hand_scoring(results.pose_landmarks.landmark, image_height, image_width)
                            hand_score_list.append(hand_scoring(results.pose_landmarks.landmark, image_height, image_width))
                            #cv2.putText(image, f"hand:{hand}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

                        else:
                            cv2.putText(image, 'Standing', (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                        
                        timemark = timemark + 1
                        time_stump_list.append(timemark)
                        print(time_stump_list)



                # 画像を表示
                cv2.imshow(f'{user_name}', image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break
        cap.release()

    def stop(self):
        self.stop_event.set()

if __name__ == '__main__':
  pass

