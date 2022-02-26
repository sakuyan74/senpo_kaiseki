# read_image.py
import os
from PIL import Image, ImageOps, ImageFilter
import numpy as np
from senpo_kaiseki.ocr.google_ocr_application_ext import GoogleOCRApplicationExt
from google_drive_ocr.application import Status
from typing import List, Tuple
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from senpo_kaiseki.code import ResultCode

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_PC_WIDTH = 1282
DEFAULT_PC_HEIGHT = 752
HEADER_HEIGHT = 30

DEFAULT_USER_THRESHOLD = 115

WIN_TMP_FILE = "/tmp/win.png"
WIN_TMP_RESULT_FILE = "/tmp/win_result.txt"
USER_TMP_FILE_PREFIX = "/tmp/username"
USER_TMP_FILE_SUFFIX = ".png"
USER_TMP_RESULT_FILE_PREFIX = "/tmp/username_result"
USER_TMP_RESULT_FILE_SUFFIX = ".txt"


class SenpoAnalyzer():

    def __init__(self):
        pass

    def analyze(self, fp, settings):

        result = {}

        # 画像の読み込み
        img_org = Image.open(fp)

        width = img_org.width
        height = img_org.height
        crop_list = None

        # 機種判別処理
        # エミュ判別
        img_rgb = img_org.convert("RGB")
        r, g, b = img_rgb.getpixel((3, 3))
        if r == b == g == 255:
            # エミュだけど画像サイズがおかしい時
            if width != DEFAULT_PC_WIDTH or height != DEFAULT_PC_HEIGHT:
                result["error_code"] = "E004"
                return result
            # エミュで画像サイズが正しい時
            else:
                crop_list = settings[str(DEFAULT_PC_WIDTH) + "x" + str(DEFAULT_PC_HEIGHT)]["crop_target_list"]

        # エミュじゃない場合の機種判別
        else:
            try:
                crop_list = settings[str(width) + "x" + str(height)]["crop_target_list"]
            except Exception:
                result["error_code"] = "E001"
                return result

        # 勝敗判定
        try:
            win_result = self.check_win(img_org, crop_list[0]["data"])
        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['win_result'] = win_result

        future_list = []
        with ThreadPoolExecutor(max_workers=4) as executor:

            future_list = [executor.submit(self.check_user, img_org, crop_list[item.value]["data"], item.name) for item in ResultCode]

            for future in as_completed(future_list):
                try:
                    f_result = future.result()
                    result[f_result[1]] = f_result[0]
                except Exception:
                    print("ERROR:")
                    print(traceback.format_exc())
                    result["error_code"] = "E999"
                    for f in future_list:
                        try:
                            if not f.running():
                                f.cancel()
                        except Exception:
                            continue
                    break

        return result

    def _binarize_image(self, img, range, threshold, win_lose=False) -> Image:

        # 切り取って拡大
        win_crop_range = range
        img_bin = img.crop((win_crop_range[0], win_crop_range[1], win_crop_range[2], win_crop_range[3]))

        if not win_lose:
            width = img_bin.width
            height = img_bin.height
            img_bin = img_bin.resize((width * 8, height * 8))

        # グレースケール
        img_bin = img_bin.convert("L")
        img_bin = ImageOps.invert(img_bin)

        # ２値化
        img_bin = np.array(img_bin, 'f')
        img_bin = (img_bin > threshold) * 255

        # PILのイメージに戻す
        img_bin = Image.fromarray(np.uint8(img_bin))
        img_bin = img_bin.convert("L")

        if not win_lose:
            img_bin = img_bin.filter(ImageFilter.MaxFilter(3))
            img_bin = img_bin.filter(ImageFilter.MaxFilter(3))
            img_bin = img_bin.filter(ImageFilter.MinFilter(3))
            img_bin = img_bin.filter(ImageFilter.MinFilter(3))

        return img_bin

    def _perform_ocr(self, img, upload_path, result_path) -> List[str]:
        app = GoogleOCRApplicationExt(temporary_upload=True)
        # 既存ファイル削除
        if os.path.isfile(upload_path):
            os.remove(upload_path)
        if os.path.isfile(result_path):
            os.remove(result_path)

        img.save(upload_path)

        # GoogleAPI呼び出し
        if app.perform_ocr(upload_path, result_path) == Status.ERROR:
            raise Exception("InternalError")

        # 出力されたファイルの確認
        with open(result_path, "r", encoding="utf-8_sig") as f:
            result = f.readlines()

        return result

    def check_user(self, img, range, name) -> Tuple[str, str]:
        # ユーザ名判定
        img_user = self._binarize_image(img, range, 115)

        file_path = USER_TMP_FILE_PREFIX + name + USER_TMP_FILE_SUFFIX
        result_path = USER_TMP_RESULT_FILE_PREFIX + name + USER_TMP_RESULT_FILE_SUFFIX

        try:
            result = self._perform_ocr(img_user, file_path, result_path)
        except Exception as e:
            raise e

        if len(result) >= 3:
            return result[2], name
        else:
            return None, name

    def check_win(self, img, range) -> str:
        # 勝敗判定
        img_win = self._binarize_image(img, range, 170, True)

        try:
            result = self._perform_ocr(img_win, WIN_TMP_FILE, WIN_TMP_RESULT_FILE)
        except Exception as e:
            raise e

        if len(result) == 0:
            return '勝'
        elif result[2] == '引分':
            return '引分'
        else:
            return '敗'
