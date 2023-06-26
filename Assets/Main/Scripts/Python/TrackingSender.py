"""cd assets/main/scripts/python"""
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import pandas as pd
import socket
import time
from PIL import Image

model_path = "./tasks/pose_landmarker_lite.task"

SOCKET_SETTING = ("127.0.0.1", 10800)
fps = 2.0
connectunity = True
landmark_line_ids = []


def connect():
    if connectunity == False:
        return
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SOCKET_SETTING)
    return client


def read_stream(landmarker, cap):
    if not cap.isOpened():
        return
    success, img = cap.read()
    if not success:
        return
    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    landmarker.detect_async(mp_image, int(cap.get(0)))


def result_to_coordinates(result: mp.tasks.vision.PoseLandmarkerResult):
    coordinates = [
        (landmark.x, landmark.y, landmark.z)
        for landmark in result.pose_world_landmarks[0]
    ]
    """
    0 - nose
    1 - left eye (inner)    2 - left eye    3 - left eye (outer)
    4 - right eye (inner)   5 - right eye   6 - right eye (outer)
    7 - left ear            8 - right ear
    9 - mouth (left)        10 - mouth (right)
    11 - left shoulder      12 - right shoulder
    13 - left elbow         14 - right elbow
    15 - left wrist         16 - right wrist
    17 - left pinky         18 - right pinky
    19 - left index         20 - right index
    21 - left thumb         22 - right thumb
    23 - left hip           24 - right hip
    25 - left knee          26 - right knee
    27 - left ankle         28 - right ankle
    29 - left heel          30 - right heel
    31 - left foot index    32 - right foot index
    """

    def get_mid(tuples):
        sum_x = sum_y = sum_z = 0
        for tuple in tuples:
            sum_x += tuple[0]
            sum_y += tuple[1]
            sum_z += tuple[2]
        len = len(tuples)
        return (sum_x / len, sum_y / len, sum_z / len)

    data = {}
    data["head"] = {"point": (coordinates[0])}

    return


def main():
    socket = connect()
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseOptions = mp.tasks.vision.PoseLandmarkerOptions
    PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    def sendResult(
        result: PoseLandmarkerResult, output_image: mp.Image, timestamp: int
    ):
        result_to_coordinates(result)
        # socket.sendto(transform_to_json(result), SOCKET_SETTING)

    options = PoseOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=sendResult,
    )

    cap = cv2.VideoCapture(0)

    with PoseLandmarker.create_from_options(options) as landmarker:
        try:
            while True:
                read_stream(landmarker, cap)
                if cv2.waitKey(5) & 0xFF == ord("q"):
                    break
        finally:
            cap.release()
            print("end")
            cv2.destroyAllWindows()


# 顔のランドマーク
def face(results, annotated_image, label, csv):
    if results.face_landmarks:
        # ランドマークを描画する
        mp_drawing.draw_landmarks(
            image=annotated_image,
            landmark_list=results.face_landmarks,
            connections=mp_holistic.FACEMESH_TESSELATION,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=drawing_spec,
        )

        for index, landmark in enumerate(results.face_landmarks.landmark):
            label.append("face_" + str(index) + "_x")
            label.append("face_" + str(index) + "_y")
            label.append("face_" + str(index) + "_z")
            csv.append(landmark.x)
            csv.append(landmark.y)
            csv.append(landmark.z)

    else:  # 検出されなかったら欠損値nanを登録する
        for index in range(468):
            label.append("face_" + str(index) + "_x")
            label.append("face_" + str(index) + "_y")
            label.append("face_" + str(index) + "_z")
            for _ in range(3):
                csv.append(np.nan)
    return label, csv


# 右手のランドマーク
def r_hand(results, annotated_image, label, csv):
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            image=annotated_image,
            landmark_list=results.right_hand_landmarks,
            connections=mp_holistic.HAND_CONNECTIONS,
        )

        for index, landmark in enumerate(results.right_hand_landmarks.landmark):
            label.append("r_hand_" + str(index) + "_x")
            label.append("r_hand_" + str(index) + "_y")
            label.append("r_hand_" + str(index) + "_z")
            csv.append(landmark.x)
            csv.append(landmark.y)
            csv.append(landmark.z)

    else:
        for index in range(21):
            label.append("r_hand_" + str(index) + "_x")
            label.append("r_hand_" + str(index) + "_y")
            label.append("r_hand_" + str(index) + "_z")
            for _ in range(3):
                csv.append(np.nan)
    return label, csv


# 左手のランドマーク
def l_hand(results, annotated_image, label, csv):
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            image=annotated_image,
            landmark_list=results.left_hand_landmarks,
            connections=mp_holistic.HAND_CONNECTIONS,
        )

        for index, landmark in enumerate(results.left_hand_landmarks.landmark):
            label.append("l_hand_" + str(index) + "_x")
            label.append("l_hand_" + str(index) + "_y")
            label.append("l_hand_" + str(index) + "_z")
            csv.append(landmark.x)
            csv.append(landmark.y)
            csv.append(landmark.z)

    else:
        for index in range(21):
            label.append("l_hand_" + str(index) + "_x")
            label.append("l_hand_" + str(index) + "_y")
            label.append("l_hand_" + str(index) + "_z")
            for _ in range(3):
                csv.append(np.nan)

    return label, csv


# 姿勢のランドマーク
def pose(results, annotated_image, label, csv):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image=annotated_image,
            landmark_list=results.pose_landmarks,
            connections=mp_holistic.POSE_CONNECTIONS,
        )

        for index, landmark in enumerate(results.pose_landmarks.landmark):
            label.append("pose_" + str(index) + "_x")
            label.append("pose_" + str(index) + "_y")
            label.append("pose_" + str(index) + "_z")
            csv.append(landmark.x)
            csv.append(landmark.y)
            csv.append(landmark.z)

    else:
        for index in range(33):
            label.append("pose_" + str(index) + "_x")
            label.append("pose_" + str(index) + "_y")
            label.append("pose_" + str(index) + "_z")
            for _ in range(3):
                csv.append(np.nan)

    return label, csv


# imageに対してmediapipeでランドマークを表示、出力する
def landmark(image):
    results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    annotated_image = image.copy()

    label = []
    csv = []

    # 姿勢→顔→右手→左手の順番でランドマーク取得
    label, csv = pose(results, annotated_image, label, csv)
    label, csv = face(results, annotated_image, label, csv)
    label, csv = r_hand(results, annotated_image, label, csv)
    label, csv = l_hand(results, annotated_image, label, csv)

    df = pd.DataFrame([csv], columns=label)

    return df, annotated_image


if __name__ == "__main__":
    main()
