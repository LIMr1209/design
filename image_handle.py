import os
from PIL import Image
import sys

path = "C:\\Users\\aaa10\\Desktop\\image\\" + sys.argv[1] + "_veer"
for i in os.listdir(path):
    try:
        image = Image.open(path + '\\' + i)
        width = image.size[0]  # 图片大小
        height = image.size[1]
        new_image = image.crop((0, 0, width, height - 80))
        new_image.save(path + '\\' + i)
    except:
        continue
