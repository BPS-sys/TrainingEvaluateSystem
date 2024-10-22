import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def is_good(landmarks, image_width, threshold=80):
  right_knee_x = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * image_width
  left_knee_x = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * image_width
  right_ankle_x = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * image_width
  left_ankle_x = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * image_width

  left_diff = abs(left_knee_x - left_ankle_x)
  right_diff = abs(right_knee_x - right_ankle_x)

  if left_diff < threshold and right_diff < threshold:
    return True
  return False

# Webカメラ入力の場合：
cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    last_time = time.time()  # 最後に座標を取得した時間を記録
    while cap.isOpened():
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

        # 5秒ごとに座標を取得する
        current_time = time.time()
        if current_time - last_time < 5:
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
                if is_good(results.pose_landmarks.landmark, image_width):
                  cv2.putText(image, 'good', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                else:
                  cv2.putText(image, 'bad', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        # 画像を表示
        cv2.imshow('Selected Landmarks', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
