# import os
# from PIL import Image
# import sys
#
# path = "C:\\Users\\aaa10\\Desktop\\image\\" + sys.argv[1] + "_veer"
# for i in os.listdir(path):
#     try:
#         image = Image.open(path + '\\' + i)
#         width = image.size[0]  # 图片大小
#         height = image.size[1]
#         new_image = image.crop((0, 0, width, height - 80))
#         new_image.save(path + '\\' + i)
#     except:
#         continue

import os
from PIL import Image
path = "C:\\Users\\aaa10\\Desktop\\lgx_front_new"
path_new = "C:\\Users\\aaa10\\Desktop\\image\\拉杆箱_rimowa_new"
for i in os.listdir(path):
    im = Image.open(path+'\\'+i)
    print(im.mode)
    # if im.mode=="RGBA":
    #     im.load()  # required for png.split()
    #     background = Image.new("RGB", im.size, (255, 255, 255))
    #     background.paste(im, mask=im.split()[3])  # 3 is the alpha channel
    #     im = background
    # im.save(path_new+'\\'+i)