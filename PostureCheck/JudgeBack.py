import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# 特定のランドマークのみ（鼻、肩、腰）を表示
landmarks_to_display = [
    mp_pose.PoseLandmark.NOSE,            # 鼻
    mp_pose.PoseLandmark.LEFT_SHOULDER,   # 左肩
    mp_pose.PoseLandmark.RIGHT_SHOULDER,  # 右肩
    mp_pose.PoseLandmark.LEFT_HIP,        # 左腰
    mp_pose.PoseLandmark.RIGHT_HIP        # 右腰
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

    if diff < 20:
        return 'Perfect'
    elif diff < 50:
        return 'Good'
    else:
        return 'Bad'

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

        # 自撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        # 画像にポーズアノテーションを描画
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            image_height, image_width, _ = image.shape

            # 鼻、肩、腰のX座標を描画
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

            # 姿勢が良いかを判定
            posture = posture_quality(results.pose_landmarks.landmark, image_width)
            cv2.putText(image, f'Posture: {posture}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # ウィンドウに画像を表示
        cv2.imshow('MediaPipe Pose', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
