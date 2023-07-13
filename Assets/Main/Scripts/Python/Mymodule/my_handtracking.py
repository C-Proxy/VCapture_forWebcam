from contextlib import contextmanager
import mediapipe as mp

model_path = "./tasks/hand_landmarker_heavy.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLMOptions = mp.tasks.vision.HandLandmarkerOptions
HandLMResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


def get_options(callback):
    options = HandLMOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=callback,
    )


def get_track_result(result):
    return


@contextmanager
def create_handlandmarker(callback_send):
    def callback(result: HandLMResult, output_image: mp.Image, timestamp: int):
        if len(result.hand_landmarks) == 0:
            print("No hand detected.")
            return
        callback_send(get_track_result(result))

    options = get_options(callback)
    with HandLandmarker.create_from_options(options) as hlm:
        yield hlm
