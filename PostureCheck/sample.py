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
      # ビデオをロードする場合は、「continue」ではなく「break」を使用してください
      continue

    # 後で自分撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # パフォーマンスを向上させるには、オプションで、参照渡しのためにイメージを書き込み不可としてマーク
    image.flags.writeable = False
    results = pose.process(image) 

    # 画像にポーズアノテーションを描画
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow('MediaPipe Pose', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()