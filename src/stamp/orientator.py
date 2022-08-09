from utils.google_ocr import GoogleVisionAPI
from utils.folder_file_manager import log_print
from settings import ROTATION_Y_THREAD


class StampOrientation:
    def __init__(self):
        self.google_api = GoogleVisionAPI()

    def estimate_rotate_angle(self, frame_path):
        init_data = self.google_api.detect_text(path=frame_path)
        word_status = {"normal": 0, "clock": 0, "counter_clock": 0, "reflection": 0}
        if init_data != {}:
            for j_res in init_data["textAnnotations"][1:]:
                try:
                    j_res_vertices = j_res["boundingPoly"]["vertices"]
                    if abs(j_res_vertices[0]["y"] - j_res_vertices[1]["y"]) > ROTATION_Y_THREAD:
                        if j_res_vertices[0]["y"] > j_res_vertices[1]["y"]:
                            word_status["clock"] += 1
                        else:
                            word_status["counter_clock"] += 1
                    else:
                        if j_res_vertices[0]["x"] > j_res_vertices[1]["x"]:
                            word_status["reflection"] += 1
                        else:
                            word_status["normal"] += 1
                except Exception as e:
                    print(e)
                    log_print(info_str=e, file_path="error.log")
                    continue

            rotate_keys = list(word_status.keys())
            status_nums = []
            for w_s_key in word_status.keys():
                status_nums.append(word_status[w_s_key])
            rotation_res = rotate_keys[status_nums.index(max(status_nums))]
        else:
            rotation_res = "normal"

        return rotation_res


if __name__ == '__main__':
    StampOrientation().estimate_rotate_angle(
        frame_path="")
