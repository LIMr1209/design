import os
from PIL import Image

# from aip import AipImageClassify
#
# APP_ID = "17887227"
# API_KEY = "HXkluVYkuRL1PURlsa973vsl"
# SECRET_KEY = "khKaBZEkN2EnDoeRkU18pGbBF71CH2Fd"

# client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
path = "C:\\Users\\aaa10\\Desktop\\拉杆箱_待处理"
for i in os.listdir(path):
    try:
        img = Image.open(path + '\\' + i)
        # rgb_data = (img.getpixel((795, 5)))
        # for x in range(0, 420):
        #     for y in range(0, 140):
        #         img.putpixel((x, y), rgb_data)
        # img.save(path + '\\' + i)

        if img.size == (400,400):
            rgb_data = (img.getpixel((395, 5)))
            for x in range(0, 70):
                for y in range(0, 80):
                    img.putpixel((x, y), rgb_data)
            img.save(path + '\\' + i)
        # elif img.size == (750,750):
        #     rgb_data = (img.getpixel((745, 5)))
        #     for x in range(0, 200):
        #         for y in range(0, 200):
        #             img.putpixel((x, y), rgb_data)
        #     img.save(path + '\\' + i)
        # elif img.size == (750,714):
        #     rgb_data = (img.getpixel((745, 5)))
        #     for x in range(0, 200):
        #         for y in range(0, 100):
        #             img.putpixel((x, y), rgb_data)
        #     img.save(path + '\\' + i)
    except Exception as e:
        print(i)
        continue

# img = Image.open("0a0fc813e95de6fc.jpg")
# rgb_data = (img.getpixel((750, 400)))

# with open("0a0fc813e95de6fc.jpg", "rb") as fp:
#     # 调用图像主体检测
#     options = dict()
#     options["with_face"] = 0
#     response = client.objectDetect(fp.read(), options)
#     param = response["result"]
# param = {'width': 396, 'top': 80, 'left': 188, 'height': 652}
# for x in range(0, 800):
#     for y in range(0, 800):
#         if x < 188 or x > 396+188 or y<80 or y>652+88:
#             img.putpixel((x, y), rgb_data)
# img.save('test.jpg')


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