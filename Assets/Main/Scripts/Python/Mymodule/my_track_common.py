class TrackSetting:
    mode = ""
    detect_flags = {"Pose": False, "Hand": False}

    def __init__(self, mode):
        self.mode = mode

    def set_detection_flag(self, tag: str, flag: bool) -> None:
        f = self.detect_flags[tag]
        # print(f"tag:{tag}-f:{f},flag:{flag}")
        if flag ^ f:
            print(f"{tag}:{flag}")
            self.detect_flags[tag] = flag
