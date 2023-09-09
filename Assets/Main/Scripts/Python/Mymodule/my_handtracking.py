from contextlib import contextmanager
import numpy as np
import mediapipe as mp

import Mymodule.my_quaternion as my_quat
from Mymodule.my_tracker import TrackSetting

ENABLE_FLIP = True
ROOT_EFFECT = 0.5

model_path = "./tasks/hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLMOptions = mp.tasks.vision.HandLandmarkerOptions
HandLMResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


class HandData:
    category: str
    wrist: np.ndarray
    fingers: np.ndarray

    def __init__(self, category: str, wrist: np.ndarray, fingers: np.ndarray) -> None:
        if ENABLE_FLIP:
            self.category = "Right" if category == "Left" else "Left"
        else:
            self.category = category
        self.wrist = wrist
        self.fingers = fingers

    def is_left(self) -> bool:
        return self.category == "Left"

    def get_hand_axis(self) -> tuple[np.ndarray, np.ndarray]:
        index_mp = self.fingers[1, 0]
        ring_mp = self.fingers[4, 0]
        forward = index_mp + ring_mp - self.wrist * 2
        if self.is_left:
            right = my_quat.normalize(index_mp - ring_mp)
        else:
            right = my_quat.normalize(ring_mp - index_mp)
        return forward, right

    def get_deltas_forward(self) -> np.ndarray:
        return self.fingers[:, :-1] - self.fingers[:, 1:]

    def get_deltas_mp(self, keepdims=False) -> np.ndarray:
        if keepdims:
            mp_list = self.fingers[:, 0:1]
        else:
            mp_list = self.fingers[:, 0]
        return mp_list[:-1] - mp_list[1:]

    def to_vector3_list(self) -> list:
        return [
            {"x": bone[0], "y": bone[1], "z": bone[2]}
            for bone in np.vstack([self.wrist, self.fingers.reshape(20, 3)])
        ]

    def to_local_vector3_list(self) -> list:
        return [
            {"x": landmark[0], "y": landmark[1], "z": landmark[2]}
            for landmark in np.insert(
                self.fingers.reshape(20, 3),
                0,
            )
        ]

    def get_quaternions(self):
        forward, right_finger = self.get_hand_axis()
        q_wrist = my_quat.get_look_quat_zx(forward, right_finger)
        n_forward_joint = my_quat.normalize(self.get_deltas_forward())
        delta_mp = self.get_deltas_mp(True)
        if not self.is_left:
            delta_mp = -delta_mp

        n_right_root = my_quat.normalize(
            my_quat.orthogonalize(
                np.insert(delta_mp, 3, delta_mp[2], 0),
                n_forward_joint[:, 0:1],
            )
        )
        print(f"cross:{np.cross(n_forward_joint[:,1:],n_forward_joint[:,:-1]).shape}")
        right_joint = my_quat.direction_synchronize(
            np.cross(n_forward_joint[:, 1:], n_forward_joint[:, :-1]),
            n_right_root,
        )
        print(f"joint:{right_joint.shape}")
        right_finger = n_right_root * ROOT_EFFECT + np.sum(right_joint, axis=1) * (
            (1 - ROOT_EFFECT) / 3
        )
        return q_wrist, [
            [my_quat.get_look_quat_zx(forward, right) for forward in finger]
            for finger, right in zip(n_forward_joint, right_finger)
        ]


def get_options(callback):
    return HandLMOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=callback,
    )


def result_to_hands(result: HandLMResult) -> list[HandData]:
    return [
        landmarks_to_hand(landmarks, handedness[0].category_name)
        for handedness, landmarks in zip(result.handedness, result.hand_world_landmarks)
    ]


def landmarks_to_hand(landmarks, category: str) -> HandData:
    bones = np.array(
        [[-landmark.x, -landmark.y, -landmark.z] for landmark in landmarks]
    )
    return HandData(category, bones[0], bones[1:].reshape(5, 4, 3))


def hand_to_transforms(hand: HandData):
    wrist, finger_all = hand.get_quaternions()
    return {
        "Wrist": my_quat.quat_to_rotation(wrist),
        "Finger": [
            [my_quat.quat_to_rotation(q) for q in finger] for finger in finger_all
        ],
    }


def get_track_results(result: HandLMResult, setting: TrackSetting):
    mode = setting.mode
    hands = result_to_hands(result)
    if mode == "Transform":
        return [
            (hand_to_transforms(hand), f"{hand.category}HandTransform")
            for hand in hands
        ]
    elif mode == "Position":
        return [
            ({"landmarks": hand.to_vector3_list()}, f"{hand.category}HandPosition")
            for hand in hands
        ]

    return


@contextmanager
def create_handlandmarker(setting: TrackSetting, callback_send):
    def callback(result: HandLMResult, output_image: mp.Image, timestamp: int):
        if len(result.hand_landmarks) == 0:
            setting.set_detection_flag("Hand", False)
        else:
            try:
                setting.set_detection_flag("Hand", True)
                for result_track, tag in get_track_results(result, setting):
                    callback_send(result_track, tag)
            except Exception as e:
                print(e)

    options = get_options(callback)
    with HandLandmarker.create_from_options(options) as hlm:
        yield hlm
