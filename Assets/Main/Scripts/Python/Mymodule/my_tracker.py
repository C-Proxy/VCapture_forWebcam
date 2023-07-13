from contextlib import contextmanager
import mediapipe as mp
import cv2

import Mymodule.my_posetracking as my_track_p
import Mymodule.my_handtracking as my_track_h


class Tracker:
    cap = None
    landmarkers = []

    def __init__(self, *landmarkers):
        self.landmarkers = landmarkers
        return self

    def read_stream(self, image: mp.Image, stamp: int):
        for landmarker in self.landmarkers:
            landmarker.detect_async(image, stamp)


@contextmanager
def create_landmarker_pose(mode: str, callback):
    with my_track_p.create_poselandmarker(mode, callback) as tracker_pose:
        yield tracker_pose


@contextmanager
def create_landmarker_hand(callback):
    with my_track_h.create_handlandmarker(callback) as tracker_hand:
        yield tracker_hand
