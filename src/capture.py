import ocr
import io
import mss
from PIL import Image


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

result = ocr.ocr_recognition(img_data)