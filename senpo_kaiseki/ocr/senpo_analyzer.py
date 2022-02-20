# read_image.py
import os
from PIL import Image, ImageOps
import numpy as np
from senpo_kaiseki.ocr.google_ocr_application_ext import GoogleOCRApplicationExt
from google_drive_ocr.application import Status

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_PC_WIDTH = 1282
DEFAULT_PC_HEIGHT = 752
HEADER_HEIGHT = 30

WIN_TMP_FILE = "/tmp/win.png"
WIN_TMP_RESULT_FILE = "/tmp/win_result.txt"
TMP_SECRET = "/tmp/client_secret.json"


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
        return result

        # 線画抽出
        '''
        img_gray2 = img_gray.filter(ImageFilter.MaxFilter(5))
        senga_inv = ImageChops.difference(img_gray, img_gray2)
        senga = ImageOps.invert(senga_inv)
        '''

    def check_win(self, img, range) -> str:
        # 勝敗判定
        win_crop_range = range
        img_win = img.crop((win_crop_range[0], win_crop_range[1], win_crop_range[2], win_crop_range[3]))

        # グレースケール
        img_win = img_win.convert("L")
        img_win = ImageOps.invert(img_win)

        # ２値化
        img_win = np.array(img_win, 'f')
        img_win = (img_win > 170) * 255

        # PILのイメージに戻す
        img_win = Image.fromarray(np.uint8(img_win))
        img_win = img_win.convert("L")

        # 既存ファイル削除
        if os.path.isfile(WIN_TMP_FILE):
            os.remove(WIN_TMP_FILE)
        if os.path.isfile(WIN_TMP_RESULT_FILE):
            os.remove(WIN_TMP_RESULT_FILE)

        # GoogleAPI呼び出し
        img_win.save(WIN_TMP_FILE)
        # img_win.show()
        if self.app.perform_ocr(WIN_TMP_FILE, WIN_TMP_RESULT_FILE) == Status.ERROR:
            raise Exception("InternalError")

        # 出力されたファイルの確認
        with open(WIN_TMP_RESULT_FILE, "r", encoding="utf-8_sig") as f:
            result = f.readlines()

        if len(result) == 0:
            return '勝'
        elif result[2] == '引分':
            return '引分'
        else:
            return '敗'
