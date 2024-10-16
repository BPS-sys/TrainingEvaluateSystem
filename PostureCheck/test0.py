import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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

        # 後で自分撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        # 画像にポーズアノテーションを描画
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            image_height, image_width, _ = image.shape

            # 描画する特定のランドマークを定義
            landmarks_to_draw = [
                mp_pose.PoseLandmark.NOSE,
                mp_pose.PoseLandmark.LEFT_EYE,
                mp_pose.PoseLandmark.RIGHT_EYE,
                mp_pose.PoseLandmark.LEFT_SHOULDER,
                mp_pose.PoseLandmark.RIGHT_SHOULDER
            ]

            # 選択したランドマークだけを描画
            for landmark in landmarks_to_draw:
                landmark_idx = landmark.value
                lm = results.pose_landmarks.landmark[landmark_idx]
                cx, cy = int(lm.x * image_width), int(lm.y * image_height)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)

        # ウィンドウに画像を表示
        cv2.imshow('MediaPipe Pose', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
