from paddleocr import PaddleOCR, draw_ocr
import global_variable as glv
from PIL import Image
import io
import numpy as np
import os
import time



# need to run only once to download and load model into memory
ocr = PaddleOCR(use_mp=True, use_angle_cls=False, precision="fp32", lang="ch")


def ocr_recognition(img_data):

    img_path = Image.open(io.BytesIO(img_data))
    img_array = np.array(img_path)
    result = ocr.ocr(img_array)

    if not glv.get("devmode"):
        print("禁止控制台输出")
        from paddleocr import paddleocr
        import logging
        paddleocr.logging.disable(logging.DEBUG)

    if glv.get("devmode"):
        print("已导出")
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
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
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

    return result
