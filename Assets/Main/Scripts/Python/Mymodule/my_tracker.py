from contextlib import contextmanager
import mediapipe as mp
import cv2

from Mymodule.my_track_common import TrackSetting
import Mymodule.my_posetracking as my_track_p
import Mymodule.my_handtracking as my_track_h


class Tracker:
    setting: TrackSetting = None
    landmarkers = []

    def __init__(self, setting: TrackSetting, *landmarkers):
        self.setting = setting
        self.landmarkers = landmarkers

    def read_capture(self, cap):
        success, image, stamp = self.get_mp_capture(cap)
        if success:
            for landmarker in self.landmarkers:
                landmarker.detect_async(image, stamp)
        else:
            print("Capture failed.")

    def get_mp_capture(self, cap) -> tuple[bool, mp.Image, int]:
        if not cap.isOpened():
            return False, None, None
        success, img = cap.read()
        if not success:
            return False, None, None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = cv2.flip(img, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        return True, mp_image, int(cap.get(0))


@contextmanager
def create_tracker(setting: TrackSetting, callback_sender):
    with (
        create_landmarker_pose(setting, callback_sender) as lm_pose,
        create_landmarker_hand(setting, callback_sender) as lm_hand,
    ):
        yield Tracker(setting, lm_pose, lm_hand)


@contextmanager
def create_landmarker_pose(setting: TrackSetting, callback):
    with my_track_p.create_poselandmarker(setting, callback) as lm_pose:
        yield lm_pose


@contextmanager
def create_landmarker_hand(setting: TrackSetting, callback):
    with my_track_h.create_handlandmarker(setting, callback) as lm_hand:
        yield lm_hand
