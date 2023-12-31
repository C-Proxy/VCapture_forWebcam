"""
cd assets/main/scripts/python
py trackingsender.py
"""
import json
import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import socket
import time

import Mymodule.my_tracker as my_tracker
from Mymodule.my_track_common import TrackSetting


SOCKET_SETTING = ("127.0.0.1", 10801)
# SEND_MODE = "Position"
SEND_MODE = "Transform"
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


def trans_to_json(content, tag: str) -> str:
    return json.dumps({"tag": tag, "content": json.dumps(content)}).encode("utf-8")


def send_result(socket: socket.socket, track_result, tag: str):
    socket.sendto(trans_to_json(track_result, tag), SOCKET_SETTING)


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


def display_result(image: mp.Image, result: PoseLMResult):
    if DISPLAY_RESULT:
        img = draw_landmarks_on_image(image.numpy_view(), result)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("Result", img)
        cv2.waitKey(1)


def main():
    wait_value = 1 / fps
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(SOCKET_SETTING)
        cap = cv2.VideoCapture(0)
        setting: TrackSetting = TrackSetting(SEND_MODE)

        def callback(result, tag: str):
            try:
                send_result(sock, result, tag)
            except Exception as e:
                print(e)

        with my_tracker.create_tracker(setting, callback) as tracker:
            try:
                while True:
                    tracker.read_capture(cap)
                    time.sleep(wait_value)
            except Exception as e:
                print(e)
            finally:
                cap.release()
                print("end")


if __name__ == "__main__":
    main()
