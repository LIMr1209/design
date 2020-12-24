# data = open("design/log.txt",encoding='utf-8')
# # line = data.readline()
# # while line:
# #     print(line)
#
# s=data.read()
# import re
# d = re.findall("Spider error processing <GET (.*)>",s)
# print(d)
# print(len(d))
category = [
    {'id': 320, 'label': 'Advertising', 'selectable': True},
    {'id': 295, 'label': 'Apps/Software', 'selectable': True},
    {'id': 390, 'label': 'Architecture', 'selectable': True},
    {'id': 56, 'label': 'Audio', 'selectable': True},
    {'id': 587, 'label': 'Automobiles', 'selectable': True},
    {'id': 583, 'label': 'Aviation', 'selectable': False},
    {'id': 44, 'label': 'Babies/Kids', 'selectable': True},
    {'id': 168, 'label': 'Bath', 'selectable': True}, {'id': 522, 'label': 'Bicycles', 'selectable': True},
    {'id': 578, 'label': 'Branding', 'selectable': True},
    {'id': 179, 'label': 'Building Technology', 'selectable': True},
    {'id': 74, 'label': 'Cameras', 'selectable': True},
    {'id': 594, 'label': 'Caravans', 'selectable': False},
    {'id': 602, 'label': 'Commercial Vehicles', 'selectable': True},
    {'id': 93, 'label': 'Computer', 'selectable': True},
    {'id': 371, 'label': 'Concepts', 'selectable': True},
    {'id': 561, 'label': 'Erotic Toys', 'selectable': False},
    {'id': 332, 'label': 'Events', 'selectable': True},
    {'id': 618, 'label': 'Eyeglasses', 'selectable': True},
    {'id': 425, 'label': 'Fashion', 'selectable': True},
    {'id': 306, 'label': 'Film/Video', 'selectable': True},
    {'id': 559, 'label': 'Garden', 'selectable': True},
    {'id': 224, 'label': 'Health/Medical', 'selectable': True},
    {'id': 542, 'label': 'Home Appliances', 'selectable': True},
    {'id': 135, 'label': 'Home Furniture', 'selectable': True},
    {'id': 233, 'label': 'Industry', 'selectable': True},
    {'id': 333, 'label': 'Interior Design', 'selectable': True},
    {'id': 142, 'label': 'Kitchen', 'selectable': True},
    {'id': 129, 'label': 'Lighting', 'selectable': True},
    {'id': 615, 'label': 'Luggage/Bags', 'selectable': True},
    {'id': 608, 'label': 'Motorbikes', 'selectable': True},
    {'id': 558, 'label': 'Music', 'selectable': True},
    {'id': 118, 'label': 'Office', 'selectable': True},
    {'id': 466, 'label': 'Outdoor', 'selectable': True},
    {'id': 400, 'label': 'Packaging', 'selectable': True},
    {'id': 736, 'label': 'Personal Use', 'selectable': True},
    {'id': 617, 'label': 'Pet supplies', 'selectable': True},
    {'id': 432, 'label': 'Photography', 'selectable': True},
    {'id': 317, 'label': 'Publications', 'selectable': True},
    {'id': 198, 'label': 'Public Design', 'selectable': True},
    {'id': 590, 'label': 'Public Transport', 'selectable': True},
    {'id': 382, 'label': 'Service Design', 'selectable': True},
    {'id': 611, 'label': 'Ships/Boats', 'selectable': True},
    {'id': 597, 'label': 'Special Vehicles', 'selectable': False},
    {'id': 560, 'label': 'Sports', 'selectable': True},
    {'id': 548, 'label': 'Tableware', 'selectable': True},
    {'id': 82, 'label': 'Telecoms', 'selectable': True},
    {'id': 673, 'label': 'Tools', 'selectable': True},
    {'id': 68, 'label': 'TV/Video', 'selectable': True},
    {'id': 740, 'label': 'User Interfaces (UI)', 'selectable': True},
    {'id': 247, 'label': 'Walls/Floor', 'selectable': True},
    {'id': 52, 'label': 'Watches/Jewelry', 'selectable': True},
    {'id': 282, 'label': 'Websites', 'selectable': True}
]
category_list = [
    {'name': "Audio", 'opalus_id': 276, "tag": '音频',},
    {'name': "Automobiles", 'opalus_id': 282, "tag": '汽车'},
    {'name': "Aviation", 'opalus_id': 282, "tag": '航空业'},
    {'name': "Babies/Kids", 'opalus_id': 285, "tag": '婴儿儿童'},
    {'name': "Office", 'opalus_id': 277, "tag": '办公'},
    {'name': "Music", 'opalus_id': 276, "tag": '音乐'},
    {'name': "Motorbikes", 'opalus_id': 282, "tag": '摩托车'},
    {'name': "Luggage/Bags", 'opalus_id': 285, "tag": '行李/包'},
    {'name': "Lighting", 'opalus_id': 288, "tag": '灯具'},
    {'name': "Kitchen", 'opalus_id': 278, "tag": '厨房'},
    {'name': "Industry", 'opalus_id': 280, "tag": '工业'},
    {'name': "Home Furniture", 'opalus_id': 281, "tag": '家庭家具'},
    {'name': "Home Appliances", 'opalus_id': 286, "tag": '家用电器'},
    {'name': "Health/Medical", 'opalus_id': 284, "tag": '健康医疗'},
    {'name': "Garden", 'opalus_id': 285, "tag": '花园'},
    {'name': "Fashion", 'opalus_id': 285, "tag": '时装'},
    {'name': "Eyeglasses", 'opalus_id': 285, "tag": '眼镜'},
    {'name': "Erotic Toys", 'opalus_id': 285, "tag": '情趣玩具'},
    {'name': "Computer", 'opalus_id': 276, "tag": '计算机'},
    {'name': "Commercial Vehicles", 'opalus_id': 282, "tag": '商用车'},
    {'name': "Cameras", 'opalus_id': 276, "tag": '摄像机'},
    {'name': "Building Technology", 'opalus_id': 317, "tag": '建筑技术'},
    {'name': "Bicycles", 'opalus_id': 282, "tag": '自行车'},
    {'name': "Bath", 'opalus_id': 316, "tag": '卫浴'},
    {'name': "Outdoor", 'opalus_id': 290, "tag": '户外'},
    {'name': "Personal Use", 'opalus_id': 285, "tag": '个人使用'},
    {'name': "Pet supplies", 'opalus_id': 285, "tag": '宠物'},
    {'name': "Public Transport", 'opalus_id': 282, "tag": '公共设计'},
    {'name': "Ships/Boats", 'opalus_id': 282, "tag": '船舶'},
    {'name': "Sports", 'opalus_id': 278, "tag": '运动'},
    {'name': "Tableware", 'opalus_id': 282, "tag": '餐具'},
    {'name': "Telecoms", 'opalus_id': 276, "tag": '电信'},
    {'name': "Tools", 'opalus_id': 280, "tag": '工具'},
    {'name': "TV/Video", 'opalus_id': 279, "tag": '电视'},
    {'name': "Walls/Floor", 'opalus_id': 281, "tag": '墙壁/地板'},
    {'name': "Watches/Jewelry", 'opalus_id': 285, "tag": '钟表/珠宝'}
]
for i in category:
    for j in category_list:
        if i['label'] == j['name']:
            j['if_id'] = i['id']

a = 1
print(category_list)
for i in category_list:
    if 'if_id' not in i:
        print(i)