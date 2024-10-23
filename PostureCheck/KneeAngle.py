import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# 特定のランドマーク（肩、腰、膝、足首）を表示
landmarks_to_display = [
    mp_pose.PoseLandmark.LEFT_SHOULDER,   # 左肩
    mp_pose.PoseLandmark.RIGHT_SHOULDER,  # 右肩
    mp_pose.PoseLandmark.LEFT_HIP,        # 左腰
    mp_pose.PoseLandmark.RIGHT_HIP,       # 右腰
    mp_pose.PoseLandmark.LEFT_KNEE,       # 左膝
    mp_pose.PoseLandmark.RIGHT_KNEE,      # 右膝
    mp_pose.PoseLandmark.LEFT_ANKLE,      # 左足首
    mp_pose.PoseLandmark.RIGHT_ANKLE      # 右足首
]

# 座っているかどうかを判定する関数（腰と膝のY座標の差を使用）
def is_sitting(landmarks, image_height, threshold=80):
    # 必要なランドマークを取得
    left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * image_height
    right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * image_height
    left_knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * image_height
    right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * image_height

    # 腰と膝のY座標の差を計算
    left_diff = abs(left_hip_y - left_knee_y)
    right_diff = abs(right_hip_y - right_knee_y)

    # 差が閾値以下の場合は「座っている」と判定
    if left_diff < threshold and right_diff < threshold:
        return True
    return False

# 姿勢がよいかを判定する関数（肩と腰のX座標の差を使用）
def posture_quality(landmarks, image_width):
    left_shoulder_x = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image_width
    right_shoulder_x = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image_width
    left_hip_x = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * image_width
    right_hip_x = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * image_width

    # 肩と腰のX座標の差を計算
    diff = abs(left_shoulder_x - left_hip_x)

    if diff < 30:
        return '100Point'
    elif diff < 50:
        return '50Point'
    else:
        return '0Point'

# ９０度人なっているかを判定する関数（左膝と左足首のX座標の差を使用）
def posture_quality_knee_ankle(landmarks, image_width):
    left_knee_x = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * image_width
    left_ankle_x = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * image_width

    # 膝と足首のX座標の差を計算
    diff = abs(left_knee_x - left_ankle_x)

    if diff < 30:
        return '100Point'
    elif diff < 50:
        return '50Point'
    else:
        return '0Point'
#首と肩の位置
def neck_scoring(landmarks, image_height, image_width):

  #座標取得
  right_ear_x = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x * image_width
  right_shoulder_x = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image_width
  left_ear_x = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * image_height
  left_shoulder_x = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image_height

  #y軸の誤差
  left_diff = abs(left_ear_x - left_shoulder_x)
  right_diff = abs(right_ear_x - right_shoulder_x)

  if left_diff < 40 and right_diff <40:
    return '100'
  elif 40 <= left_diff <= 55 or 40 <= right_diff <= 55:
    return '50'
  else:
    return '0'

#手首と膝のy軸とz軸を検証する
def hand_scoring(landmarks, image_height, image_width):#z軸:膝=手首 y軸:膝-手首<限界値　x軸:閾値<膝-手首<限界値

  #正規化
  right_knee_x = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * image_width
  right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * image_height
  right_knee_z = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z * image_height
  right_wrist_x = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * image_width
  right_wrist_y = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * image_height
  right_wrist_z = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z * image_height

#x軸とy軸の差
  right_x_diff = abs(right_knee_x - right_wrist_x)
  right_y_diff = abs(right_knee_y - right_wrist_y)
  right_z_diff = abs(right_knee_z - right_wrist_z)

  if 30 <= right_x_diff <= 60 and 40 <= right_y_diff <= 80 and 0 <= right_z_diff <= 50:#x30~50, y40~50, z0~10
    return '100'
  elif ((20 <= right_x_diff <= 29 or 51 <= right_x_diff <= 60) and
        (30 <= right_y_diff <= 39 or 51 <= right_y_diff <= 60) and
        11 <= right_z_diff <= 20):#x20~29・51~60, y30~39,51~60, z11~20 
    return '50'
  else:
    return '0'
# Webカメラ入力の場合：
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            image_height, image_width, _ = image.shape

            # 肩、腰、膝、足首のX座標を描画
            for landmark in landmarks_to_display:
                idx = landmark.value
                landmark_x = results.pose_landmarks.landmark[idx].x * image_width  # X座標を画面上の幅にスケーリング
                cv2.putText(image, f'{landmark.name} X: {landmark_x:.2f}', (10, 30 + idx * 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # 座っているかを判定
            if is_sitting(results.pose_landmarks.landmark, image_height):
                cv2.putText(image, 'Sitting', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                cv2.putText(image, 'Standing', (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # 左膝と左足首のX座標を使って９０度になっているかを判定
            posture = posture_quality_knee_ankle(results.pose_landmarks.landmark, image_width)
            cv2.putText(image, f'Posture (Knee-Ankle): {posture}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # 姿勢が良いかを判定
            posture = posture_quality(results.pose_landmarks.landmark, image_width)
            cv2.putText(image, f'Posture: {posture}', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            #首の判定
            neck = neck_scoring(results.pose_landmarks.landmark, image_height, image_width)
            cv2.putText(image, f"neck:{neck}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
             #手首の判定
            hand = hand_scoring(results.pose_landmarks.landmark, image_height, image_width)
            cv2.putText(image, f"hand:{hand}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # ウィンドウに画像を表示
        cv2.imshow('MediaPipe Pose', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
