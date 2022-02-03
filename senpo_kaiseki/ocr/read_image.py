# read_image.py
import os
from PIL import Image
import pyocr
import pyocr.builders


def read_image():
    # pathを通す
    path_tesseract = "C:\\Program Files\\Tesseract-OCR"
    if path_tesseract not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += path_tesseract

    # OCRエンジンの取得
    tools = pyocr.get_available_tools()
    tool = tools[0]

    # 原稿画像の読み込み
    img_org = Image.open("./samplefile/sample.png")

    # 実行
    builder = pyocr.builders.TextBuilder()
    result = tool.image_to_string(img_org, lang="jpn", builder=builder)

    print(result)
