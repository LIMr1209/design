import os
from PIL import Image

# from aip import AipImageClassify
#
# APP_ID = "17887227"
# API_KEY = "HXkluVYkuRL1PURlsa973vsl"
# SECRET_KEY = "khKaBZEkN2EnDoeRkU18pGbBF71CH2Fd"

# client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
path = "C:\\Users\\aaa10\\Desktop\\耳机_待处理"
for i in os.listdir(path):
    try:
        img = Image.open(path + '\\' + i)
        rgb_data = (img.getpixel((795, 5)))
        for x in range(0, 300):
            for y in range(0, 100):
                img.putpixel((x, y), rgb_data)
        img.save(path + '\\' + i)
        # if img.size == (600,600):
        #
        #     rgb_data = (img.getpixel((555, 555)))
        #     for x in range(470, 600):
        #         for y in range(550, 600):
        #             img.putpixel((x, y), rgb_data)
        #     img.save(path + '\\' + i)
        # elif img.size == (450,450):
        #     rgb_data = (img.getpixel((445, 445)))
        #     for x in range(350, 450):
        #         for y in range(420, 450):
        #             img.putpixel((x, y), rgb_data)
        #     img.save(path + '\\' + i)
        # elif img.size == (290,290):
        #     rgb_data = (img.getpixel((285, 285)))
        #     for x in range(200, 290):
        #         for y in range(260, 290):
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
