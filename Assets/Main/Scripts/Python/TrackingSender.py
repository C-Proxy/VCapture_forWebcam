"""
cd assets/main/scripts/python
py trackingsender.py
"""
import json
from operator import itemgetter
from queue import PriorityQueue
import string
import sys
from xml.dom.minidom import TypeInfo
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import pandas as pd
import socket
import time
from PIL import Image

import Mymodule.my_quaternion as my_quat

# model_path = "./tasks/pose_landmarker_lite.task"
model_path = "./tasks/pose_landmarker_heavy.task"


SOCKET_SETTING = ("127.0.0.1", 10801)
# SEND_MODE = "Pose"
SEND_MODE = "IK"
VIEW_RESULT = False

fps = 30.0
connect_accept = False

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
list_bone_names = [
    "nose",
    "eye_inner_L",
    "eye_L",
    "eye_outer_L",
    "eye_inner_R",
    "eye_R",
    "eye_outer_R",
    "ear_L",
    "ear_R",
    "mouth_L",
    "mouth_R",
    "shoulder_L",
    "shoulder_R",
    "elbow_L",
    "elbow_R",
    "hand_L",
    "hand_R",
    "pinky_L",
    "pinky_R",
    "index_L",
    "index_R",
    "thumb_L",
    "thumb_R",
    "hip_L",
    "hip_R",
    "knee_L",
    "knee_R",
    "ankle_L",
    "ankle_R",
    "heel_L",
    "heel_R",
    "foot_index_L",
    "foot_index_R",
]
"""
    0 - nose
    1 - left ear           2 - right ear
    3 - left shoulder      4 - right shoulder
    5 - left elbow         6 - right elbow
    7 - left wrist         8 - right wrist
    9 - left pinky         10 - right pinky
    11 - left index        12 - right index
"""
list_ikbone_names = [
    "nose",
    "ear_L",
    "ear_R",
    "shoulder_L",
    "shoulder_R",
    "elbow_L",
    "elbow_R",
    "hand_L",
    "hand_R",
    "pinky_L",
    "pinky_R",
    "index_L",
    "index_R",
]
ikbone_slicer = [list_bone_names.index(bone) for bone in list_ikbone_names]

"""
0 - nose
11 - left shoulder      12 - right shoulder
13 - left elbow         14 - right elbow
15 - left wrist         16 - right wrist
17 - left pinky         18 - right pinky
19 - left index         20 - right index
21 - left thumb         22 - right thumb
23 - left hip           24 - right hip
"""
list_posebone_names = [
    "nose",
    "shoulder_L",
    "shoulder_R",
    "elbow_L",
    "elbow_R",
    "hand_L",
    "hand_R",
    "pinky_L",
    "pinky_R",
    "index_L",
    "index_R",
    "thumb_L",
    "thumb_R",
    "hip_L",
    "hip_R",
]
posebone_slicer = [list_bone_names.index(bone) for bone in list_posebone_names]

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
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    landmarker.detect_async(mp_image, int(cap.get(0)))


def landmarks_to_bones(result: PoseLMResult, slicer: list[int]) -> list[np.ndarray]:
    return itemgetter(*slicer)(
        [
            np.array([landmark.x, -landmark.y, -landmark.z])
            for landmark in result.pose_world_landmarks[0]
        ]
    )


def trans_landmarks_to_pos_ik(result: PoseLMResult):
    bones = landmarks_to_bones(result, ikbone_slicer)

    """
    0 - nose
    1 - left ear           2 - right ear
    3 - left shoulder      4 - right shoulder
    5 - left elbow         6 - right elbow
    7 - left wrist         8 - right wrist
    9 - left pinky         10 - right pinky
    11 - left index        12 - right index
    """
    nose = bones[0]
    ear_l = bones[1]
    ear_r = bones[2]
    shoulder_l = bones[3]
    shoulder_r = bones[4]
    elbow_l = bones[5]
    elbow_r = bones[6]
    hand_l = bones[7]
    hand_r = bones[8]
    pinky_l = bones[9]
    pinky_r = bones[10]
    index_l = bones[11]
    index_r = bones[12]

    head = (ear_l + ear_r) / 2
    pelvis = np.array([0.0, 0.0, 0.0])

    return {
        "Head": {
            "position": head,
            "rotation": my_quat.get_look_quat_zx(nose - head, ear_r - ear_l),
        },
        "LeftHand": {
            "position": hand_l,
            "rotation": my_quat.get_look_quat_zx(
                index_l + pinky_l - hand_l * 2, index_l - pinky_l
            ),
        },
        "RightHand": {
            "position": hand_r,
            "rotation": my_quat.get_look_quat_zx(
                pinky_r + index_r - hand_r * 2, pinky_r - index_r
            ),
        },
        "LeftElbow": {"position": elbow_l},
        "RightElbow": {"position": elbow_r},
        "Root": {
            "position": pelvis,
            "rotation": my_quat.get_look_quat_xy(
                shoulder_r - shoulder_l, shoulder_r + shoulder_l
            ),
        },
    }


def trans_landmarks_to_pos_pose(result: PoseLMResult):
    pos = [
        {"x": bone[0], "y": bone[1], "z": bone[2]}
        for bone in landmarks_to_bones(result, posebone_slicer)
    ]
    return {"landmarks": pos}


def trans_posData_to_json(data, tag: str) -> str:
    for bone in data.values():
        if "position" in bone:
            pos = bone["position"]
            bone["position"] = {"x": pos[0], "y": pos[1], "z": pos[2]}
        if "rotation" in bone:
            rot = bone["rotation"].components
            bone["rotation"] = {"w": rot[0], "x": rot[1], "y": rot[2], "z": rot[3]}
    return json.dumps({"tag": tag, "content": json.dumps(data)})
    # return json.dumps(data)


def solver_ik(result: PoseLMResult, tag: str):
    content = trans_landmarks_to_pos_ik(result)
    package = trans_posData_to_json(content, tag)
    return package


def solver_pose(result: PoseLMResult, tag: str):
    content = trans_landmarks_to_pos_pose(result)
    package = json.dumps({"tag": tag, "content": json.dumps(content)})
    return package


def send_result(socket: socket.socket, result: PoseLMResult, solver, tag: str):
    package = solver(result, tag)
    socket.sendto(package.encode("utf-8"), SOCKET_SETTING)


def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # Draw the pose landmarks.
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                )
                for landmark in pose_landmarks
            ]
        )
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style(),
        )
    return annotated_image


def main():
    wait_value = 1 / fps
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(SOCKET_SETTING)
        cap = cv2.VideoCapture(0)

        solver = {
            "IK": solver_ik,
            "Pose": solver_pose,
        }

        def track_callback(
            result: PoseLMResult, output_image: mp.Image, timestamp: int
        ):
            try:
                send_result(sock, result, solver[SEND_MODE], SEND_MODE)
                if VIEW_RESULT:
                    # img =output_image.numpy_view()
                    # img = result.segmentation_masks[0].numpy_view()
                    img = draw_landmarks_on_image(output_image.numpy_view(), result)

                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Result", img)
                    cv2.waitKey(1)
            except Exception as e:
                e_type, e_obj, e_tb = sys.exc_info()
                print(f"{e_type}:at line-{e_tb.tb_lineno}")

        options = PoseLMOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            # output_segmentation_masks=True,
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
