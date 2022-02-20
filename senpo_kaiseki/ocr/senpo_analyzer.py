# read_image.py
import os
from PIL import Image, ImageOps, ImageChops, ImageFilter
import numpy as np
from senpo_kaiseki.ocr.google_ocr_application_ext import GoogleOCRApplicationExt
from google_drive_ocr.application import Status
from typing import List, Tuple

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_PC_WIDTH = 1282
DEFAULT_PC_HEIGHT = 752
HEADER_HEIGHT = 30

WIN_TMP_FILE = "/tmp/win.png"
WIN_TMP_RESULT_FILE = "/tmp/win_result.txt"
USER_TMP_FILE = "/tep/username.png"
USER_TMP_RESULT_FILE = "/tep/username_result.txt"


class SenpoAnalyzer():

    def __init__(self):
        self.app = GoogleOCRApplicationExt()

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
            return result

        result['win_result'] = win_result

        # 味方ユーザ名抽出
        try:
            user_result = self.check_user(img_org, crop_list[1]["data"])
        except Exception:
            result["error_code"] = "E999"
            return result

        result['user_result'] = user_result

        # 敵ユーザ名抽出
        try:
            e_user_result = self.check_user(img_org, crop_list[2]["data"])
        except Exception:
            result["error_code"] = "E999"
            return result

        result['e_user_result'] = e_user_result

        return result

    def _binarize_image(self, img, range, threshold, to_senga=False) -> Image:
        # 切り取り
        win_crop_range = range
        img_bin = img.crop((win_crop_range[0], win_crop_range[1], win_crop_range[2], win_crop_range[3]))

        # グレースケール
        img_bin = img_bin.convert("L")
        img_bin = ImageOps.invert(img_bin)

        # ２値化
        img_bin = np.array(img_bin, 'f')
        img_bin = (img_bin > threshold) * 255

        # PILのイメージに戻す
        img_bin = Image.fromarray(np.uint8(img_bin))
        img_bin = img_bin.convert("L")

        if to_senga:
            img_bin2 = img_bin.filter(ImageFilter.MaxFilter(5))
            senga_inv = ImageChops.difference(img_bin, img_bin2)
            senga = ImageOps.invert(senga_inv)
            return senga

        return img_bin

    def _perform_ocr(self, upload_path, resulf_path) -> List[str]:
        # 既存ファイル削除
        if os.path.isfile(upload_path):
            os.remove(upload_path)
        if os.path.isfile(resulf_path):
            os.remove(resulf_path)

        # GoogleAPI呼び出し
        if self.app.perform_ocr(upload_path, resulf_path) == Status.ERROR:
            raise Exception("InternalError")

        # 出力されたファイルの確認
        with open(resulf_path, "r", encoding="utf-8_sig") as f:
            result = f.readlines()

        return result

    def check_user(self, img, range) -> Tuple[str]:
        # ユーザ名判定
        img_user = self._binarize_image(img, range, 115, True)
        img_user.save()

        try:
            result = self._perform_ocr(USER_TMP_FILE, USER_TMP_RESULT_FILE)
        except Exception as e:
            raise e

        if len(result) >= 3:
            return result[2]
        else:
            return '読み込みに失敗しました'

    def check_win(self, img, range) -> str:
        # 勝敗判定
        img_win = self._binarize_image(img, range, 170)
        img_win.save(WIN_TMP_FILE)

        try:
            result = self._perform_ocr(WIN_TMP_FILE, WIN_TMP_RESULT_FILE)
        except Exception as e:
            raise e

        if len(result) == 0:
            return '勝'
        elif result[2] == '引分':
            return '引分'
        else:
            return '敗'
