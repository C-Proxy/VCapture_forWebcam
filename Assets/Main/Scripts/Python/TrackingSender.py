"""
cd assets/main/scripts/python
py trackingsender.py
"""
import json
import sys
import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import socket
import time

import Mymodule.my_posetracking as my_plm


SOCKET_SETTING = ("127.0.0.1", 10801)
# SEND_MODE = "Pose"
SEND_MODE = "IK"
DISPLAY_RESULT = False

fps = 30.0
connectable_to_unity = False

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLMResult = mp.tasks.vision.PoseLandmarkerResult
PoseLMOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def connect():
    if connectable_to_unity == False:
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
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    landmarker.detect_async(mp_image, int(cap.get(0)))


def trans_posData_to_json(data, tag: str) -> str:
    for bone in data.values():
        if "position" in bone:
            pos = bone["position"]
            bone["position"] = {"x": pos[0], "y": pos[1], "z": pos[2]}
        if "rotation" in bone:
            rot = bone["rotation"].components
            bone["rotation"] = {"w": rot[0], "x": rot[1], "y": rot[2], "z": rot[3]}
    return json.dumps({"tag": tag, "content": json.dumps(data)})


def packager_ik(result: PoseLMResult, tag: str):
    content = my_plm.get_transforms_ik(result)
    package = trans_posData_to_json(content, tag)
    return package


def packager_pose(result: PoseLMResult, tag: str):
    content = my_plm.get_positions_pose(result)
    package = json.dumps({"tag": tag, "content": json.dumps(content)})
    return package


def send_result(socket: socket.socket, result: PoseLMResult, packager, tag: str):
    try:
        package = packager(result, tag)
    except Exception as e:
        print(e.args)
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

        packager = {
            "IK": packager_ik,
            "Pose": packager_pose,
        }

        def tracking_callback(
            result: PoseLMResult, output_image: mp.Image, timestamp: int
        ):
            if len(result.pose_landmarks) == 0:
                print("No Pose detected.")
                return
            try:
                send_result(sock, result, packager[SEND_MODE], SEND_MODE)
                if DISPLAY_RESULT:
                    # img =output_image.numpy_view()
                    # img = result.segmentation_masks[0].numpy_view()
                    img = draw_landmarks_on_image(output_image.numpy_view(), result)

                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Result", img)
                    cv2.waitKey(1)
            except Exception as e:
                e_type, e_obj, e_tb = sys.exc_info()
                print(f"{e_type}:at line-{e_tb.tb_lineno}")

        options = my_plm.get_options(tracking_callback)
        with PoseLandmarker.create_from_options(options) as landmarker:
            try:
                while True:
                    read_stream(landmarker, cap)
                    time.sleep(wait_value)
            finally:
                cap.release()
                print("end")


if __name__ == "__main__":
    main()
