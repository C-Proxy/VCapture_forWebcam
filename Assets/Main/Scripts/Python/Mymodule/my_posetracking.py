from contextlib import contextmanager
from email import contentmanager
from operator import itemgetter
import numpy as np
import mediapipe as mp

import Mymodule.my_quaternion as my_quat

# model_path = "./tasks/pose_landmarker_lite.task"
model_path = "./tasks/pose_landmarker_heavy.task"

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLMResult = mp.tasks.vision.PoseLandmarkerResult
PoseLMOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

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

list_landmark_names = [
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
list_ik_landmarks = [
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
list_pose_landmarks = [
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


def get_options(callback):
    return PoseLMOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        # output_segmentation_masks=True,
        result_callback=callback,
    )


def result_to_landmarks(result: PoseLMResult, list_use_landmarks: list[str]):
    landmarks = itemgetter(
        *[list_landmark_names.index(landmark) for landmark in list_use_landmarks]
    )(result.pose_world_landmarks[0])
    return {
        name: np.array([bone.x, -bone.y, -bone.z])
        for name, bone in zip(list_use_landmarks, landmarks)
    }


def get_transforms_ik(result: PoseLMResult):
    landmarks = result_to_landmarks(result, list_ik_landmarks)

    """
    0 - nose
    1 - left ear           2 - right ear
    3 - left shoulder      4 - right shoulder
    5 - left elbow         6 - right elbow
    7 - left wrist         8 - right wrist
    9 - left pinky         10 - right pinky
    11 - left index        12 - right index
    """
    nose = landmarks["nose"]
    ear_l = landmarks["ear_L"]
    ear_r = landmarks["ear_R"]
    shoulder_l = landmarks["shoulder_L"]
    shoulder_r = landmarks["shoulder_R"]
    elbow_l = landmarks["elbow_L"]
    elbow_r = landmarks["elbow_R"]
    hand_l = landmarks["hand_L"]
    hand_r = landmarks["hand_R"]
    pinky_l = landmarks["pinky_L"]
    pinky_r = landmarks["pinky_R"]
    index_l = landmarks["index_L"]
    index_r = landmarks["index_R"]

    head = (ear_l + ear_r) / 2
    pelvis = np.array([0.0, 0.0, 0.0])

    transforms = {
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
    for bone in transforms.values():
        if "position" in bone:
            pos = bone["position"]
            bone["position"] = {"x": pos[0], "y": pos[1], "z": pos[2]}
        if "rotation" in bone:
            rot = bone["rotation"].components
            bone["rotation"] = {"w": rot[0], "x": rot[1], "y": rot[2], "z": rot[3]}
    return transforms


def get_positions_pose(result: PoseLMResult):
    pos = [
        {"x": landmark[0], "y": landmark[1], "z": landmark[2]}
        for landmark in result_to_landmarks(result, list_landmark_names).values()
    ]
    return {"landmarks": pos}


def get_track_result(tag: str, result: PoseLMResult):
    if tag == "IK":
        return get_transforms_ik(result)
    elif tag == "Pose":
        return get_positions_pose, (result)


@contextmanager
def create_poselandmarker(tag: str, callback_send):
    def callback(result: PoseLMResult, output_image: mp.Image, timestamp: int):
        if len(result.pose_landmarks) == 0:
            print("No Pose detected.")
            return
        callback_send(get_track_result(tag, result))

    options = get_options(callback)
    with PoseLandmarker.create_from_options(options) as plm:
        yield plm
