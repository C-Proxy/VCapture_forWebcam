"""cd assets/main/scripts/python"""
"""py trackingsender.py"""
import json
from queue import PriorityQueue
import string
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import pandas as pd
import socket
import time
from PIL import Image

import Mymodule.my_quaternion as my_quat

model_path = "./tasks/pose_landmarker_lite.task"

SOCKET_SETTING = ("127.0.0.1", 10800)
fps = 2.0
connect_accept = False
# landmark_line_ids = []

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLMOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLMResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


def connect():
    if connect_accept == False:
        return
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SOCKET_SETTING)
    return client


def read_stream(landmarker: PoseLandmarker, cap):
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


def trans_landmarks_to_posData(result: PoseLMResult):
    pos = [
        np.array([landmark.x, landmark.z, landmark.y])
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
    nose = pos[0]
    mouth_left = pos[9]
    mouth_right = pos[10]
    shoulder_left = pos[11]
    shoulder_right = pos[12]
    pelvis = np.array([pos[23], pos[24]]).mean(0)

    return {
        "head": {
            "pos": (pos[0]),
            "quat": my_quat.get_look_quat_f(
                mouth_right - mouth_left, mouth_right + mouth_left - nose * 2
            ),
        },
        "leftHand": {"pos": pos[15]},
        "rightHand": {"pos": pos[16]},
        "leftElbow": {"pos": pos[13]},
        "rightElbow": {"pos": pos[14]},
        "root": {
            "pos": pelvis,
            "quat": my_quat.get_look_quat_f(
                shoulder_right - shoulder_left,
                shoulder_right + shoulder_left - pelvis * 2,
            ),
        },
    }


def trans_posData_to_json(data) -> str:
    for bone in data.values():
        if "pos" in bone:
            bone["pos"] = bone["pos"][[0, 2, 1]].tolist()
        if "quat" in bone:
            bone["quat"] = bone["quat"].components[[0, 1, 3, 2]].tolist()
    # return json.dumps({"data": data})
    return json.dumps(data)


def send_result(socket: socket.socket, result: PoseLMResult):
    data = trans_landmarks_to_posData(result)
    json = trans_posData_to_json(data)
    print(json)
    socket.sendto(json.encode("utf-8"), SOCKET_SETTING)


def main():
    wait_value = 1 / fps
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(SOCKET_SETTING)
        cap = cv2.VideoCapture(0)

        def track_callback(
            result: PoseLMResult, output_image: mp.Image, timestamp: int
        ):
            try:
                send_result(sock, result)
            except Exception as e:
                print(e)

        options = PoseLMOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=track_callback,
        )
        with PoseLandmarker.create_from_options(options) as landmarker:
            try:
                while True:
                    read_stream(landmarker, cap)
                    time.sleep(wait_value)
            finally:
                cap.release()
                print("end")


"""
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
"""

if __name__ == "__main__":
    main()
