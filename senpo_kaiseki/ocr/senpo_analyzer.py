# read_image.py
import os
from PIL import Image, ImageOps, ImageFilter
import numpy as np
from senpo_kaiseki.ocr.google_ocr_application_ext import GoogleOCRApplicationExt
from google_drive_ocr.application import Status
from typing import List
import traceback

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_PC_WIDTH = 1282
DEFAULT_PC_HEIGHT = 752
HEADER_HEIGHT = 30

DEFAULT_USER_THRESHOLD = 115

WIN_TMP_FILE = "/tmp/win.png"
WIN_TMP_RESULT_FILE = "/tmp/win_result.txt"
USER_TMP_FILE = "/tmp/username.png"
USER_TMP_RESULT_FILE = "/tmp/username_result.txt"


class SenpoAnalyzer():

    def __init__(self):
        self.app = GoogleOCRApplicationExt(temporary_upload=False)

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

        # 味方ユーザ名抽出
        try:
            user_result = self.check_user(img_org, crop_list[1]["data"])
            if user_result is None:
                user_result = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['user_result'] = user_result

        # 敵ユーザ名抽出
        try:
            e_user_result = self.check_user(img_org, crop_list[2]["data"])
            if e_user_result is None:
                e_user_result = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_user_result'] = e_user_result

        # 敵同盟名抽出
        try:
            e_alliance = self.check_user(img_org, crop_list[3]["data"])
            if e_alliance is None:
                e_alliance = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_alliance'] = e_alliance

        # 味方レベル１抽出
        try:
            level1 = self.check_user(img_org, crop_list[4]["data"])
            if level1 is None:
                level1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['level1'] = level1

        # 味方レベル２抽出
        try:
            level2 = self.check_user(img_org, crop_list[5]["data"])
            if level2 is None:
                level2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['level2'] = level2

        # 味方レベル３抽出
        try:
            level3 = self.check_user(img_org, crop_list[6]["data"])
            if level3 is None:
                level3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['level3'] = level3

        # 敵レベル３抽出
        try:
            e_level3 = self.check_user(img_org, crop_list[7]["data"])
            if e_level3 is None:
                e_level3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_level3'] = e_level3

        # 敵レベル２抽出
        try:
            e_level2 = self.check_user(img_org, crop_list[8]["data"])
            if e_level2 is None:
                e_level2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_level2'] = e_level2

        # 敵レベル１抽出
        try:
            e_level1 = self.check_user(img_org, crop_list[9]["data"])
            if e_level1 is None:
                e_level1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_level1'] = e_level1

        # 味方主将戦法1抽出
        try:
            senpo_1_1 = self.check_user(img_org, crop_list[10]["data"])
            if senpo_1_1 is None:
                senpo_1_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_1_1'] = senpo_1_1

        # 味方主将戦法２抽出
        try:
            senpo_1_2 = self.check_user(img_org, crop_list[11]["data"])
            if senpo_1_2 is None:
                senpo_1_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_1_2'] = senpo_1_2

        # 味方主将戦法３抽出
        try:
            senpo_1_3 = self.check_user(img_org, crop_list[12]["data"])
            if senpo_1_3 is None:
                senpo_1_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_1_3'] = senpo_1_3

        # 味方副将１戦法1抽出
        try:
            senpo_2_1 = self.check_user(img_org, crop_list[13]["data"])
            if senpo_2_1 is None:
                senpo_2_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_2_1'] = senpo_2_1

        # 味方副将１戦法２抽出
        try:
            senpo_2_2 = self.check_user(img_org, crop_list[14]["data"])
            if senpo_2_2 is None:
                senpo_2_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_2_2'] = senpo_2_2

        # 味方副将１戦法３抽出
        try:
            senpo_2_3 = self.check_user(img_org, crop_list[15]["data"])
            if senpo_2_3 is None:
                senpo_2_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_2_3'] = senpo_2_3

        # 味方副将２戦法1抽出
        try:
            senpo_3_1 = self.check_user(img_org, crop_list[16]["data"])
            if senpo_3_1 is None:
                senpo_3_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_3_1'] = senpo_3_1

        # 味方副将２戦法２抽出
        try:
            senpo_3_2 = self.check_user(img_org, crop_list[17]["data"])
            if senpo_3_2 is None:
                senpo_3_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_3_2'] = senpo_3_2

        # 味方副将２戦法３抽出
        try:
            senpo_3_3 = self.check_user(img_org, crop_list[18]["data"])
            if senpo_3_3 is None:
                senpo_3_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['senpo_3_3'] = senpo_3_3

        # 敵副将２戦法1抽出
        try:
            e_senpo_3_1 = self.check_user(img_org, crop_list[19]["data"])
            if e_senpo_3_1 is None:
                e_senpo_3_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_3_1'] = e_senpo_3_1

        # 敵副将２戦法２抽出
        try:
            e_senpo_3_2 = self.check_user(img_org, crop_list[20]["data"])
            if e_senpo_3_2 is None:
                e_senpo_3_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_3_2'] = e_senpo_3_2

        # 敵副将２戦法３抽出
        try:
            e_senpo_3_3 = self.check_user(img_org, crop_list[21]["data"])
            if e_senpo_3_3 is None:
                e_senpo_3_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_3_3'] = e_senpo_3_3

        # 敵副将１戦法1抽出
        try:
            e_senpo_2_1 = self.check_user(img_org, crop_list[22]["data"])
            if e_senpo_2_1 is None:
                e_senpo_2_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_2_1'] = e_senpo_2_1

        # 敵副将１戦法２抽出
        try:
            e_senpo_2_2 = self.check_user(img_org, crop_list[23]["data"])
            if e_senpo_2_2 is None:
                e_senpo_2_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_2_2'] = e_senpo_2_2

        # 敵副将１戦法３抽出
        try:
            e_senpo_2_3 = self.check_user(img_org, crop_list[24]["data"])
            if e_senpo_2_3 is None:
                e_senpo_2_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_2_3'] = e_senpo_2_3

        # 敵主将戦法1抽出
        try:
            e_senpo_1_1 = self.check_user(img_org, crop_list[25]["data"])
            if e_senpo_1_1 is None:
                e_senpo_1_1 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_1_1'] = e_senpo_1_1

        # 敵主将戦法２抽出
        try:
            e_senpo_1_2 = self.check_user(img_org, crop_list[26]["data"])
            if e_senpo_1_2 is None:
                e_senpo_1_2 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_1_2'] = e_senpo_1_2

        # 敵主将戦法３抽出
        try:
            e_senpo_1_3 = self.check_user(img_org, crop_list[27]["data"])
            if e_senpo_1_3 is None:
                e_senpo_1_3 = '読み取れませんでした'

        except Exception:
            result["error_code"] = "E999"
            print(traceback.format_exc())
            return result

        result['e_senpo_1_3'] = e_senpo_1_3

        return result

    def _binarize_image(self, img, range, threshold) -> Image:
        # 拡大して切り取り
        width = img.width
        height = img.height

        img_bin = img.resize((width * 8, height * 8))

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

        img_bin = img_bin.filter(ImageFilter.MaxFilter(3))
        img_bin = img_bin.filter(ImageFilter.MaxFilter(3))
        img_bin = img_bin.filter(ImageFilter.MinFilter(3))
        img_bin = img_bin.filter(ImageFilter.MinFilter(3))

        return img_bin

    def _perform_ocr(self, img, upload_path, result_path) -> List[str]:
        # 既存ファイル削除
        if os.path.isfile(upload_path):
            os.remove(upload_path)
        if os.path.isfile(result_path):
            os.remove(result_path)

        img.save(upload_path)

        # GoogleAPI呼び出し
        if self.app.perform_ocr(upload_path, result_path) == Status.ERROR:
            raise Exception("InternalError")

        # 出力されたファイルの確認
        with open(result_path, "r", encoding="utf-8_sig") as f:
            result = f.readlines()

        return result

    def check_user(self, img, range) -> str:
        # ユーザ名判定
        img_user = self._binarize_image(img, range, 115)

        try:
            result = self._perform_ocr(img_user, USER_TMP_FILE, USER_TMP_RESULT_FILE)
        except Exception as e:
            raise e

        if len(result) >= 3:
            return result[2]
        else:
            return None

    def check_win(self, img, range) -> str:
        # 勝敗判定
        img_win = self._binarize_image(img, range, 170)

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
