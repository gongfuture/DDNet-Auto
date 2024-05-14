import numpy as np
from paddleocr import PaddleOCR, draw_ocr
import io
import mss
from PIL import Image
import time


devmode = True


# Copy from https://blog.csdn.net/weixin_50674989/article/details/122459230
class ImageConvert(io.BytesIO):
    "假的保存"

    def write(self, data):
        if not hasattr(self, "data"):
            self.data = b""
        self.data += data


m = mss.mss()
_monitor = m.monitors[0]  # 默认截的是全屏


def get_data(monitor=_monitor, quality=95):
    bio = ImageConvert()
    bio.name = "temp.jpg"   # 确保时jpg格式，temp这个可以改
    img = m.grab(monitor)
    pil = Image.new("RGB", img.size)
    pil.frombytes(img.rgb)
    pil.save(bio, quality=quality)  # 默认最高质量
    del img, pil
    return bio.data


img_data = get_data(_monitor)

# need to run only once to download and load model into memory
ocr = PaddleOCR(use_mp=True, use_angle_cls=False, precision="fp32", lang="ch")
img_path = Image.open(io.BytesIO(img_data))
img_array = np.array(img_path)
result = ocr.ocr(img_array)

if devmode:
    import os
    path = [
        "../log",
        "../log/outputtexts",
        "../log/resultpictures",
        "../log/logs"]
    for idx in range(len(path)):
        if not os.path.exists(path[idx]):
            os.makedirs(path[idx])
        else:
            pass
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    with open('../log/outputtexts/' + timestamp + '.txt', 'w', encoding='utf-8') as f:
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                print(line)
                f.write(str(line) + '\n')

    result = result[0]
    image = img_path.convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(
        image,
        boxes,
        txts,
        scores,
        font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('../log/resultpictures/' + timestamp + '.jpg')
