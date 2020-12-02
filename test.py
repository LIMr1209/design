import execjs
from design.utils.antiContent_Js import js
#
# with open('design/utils/anti_content_new.js', 'r', encoding='utf-8') as f:
#     js = f.read()
# anti_content = execjs.compile(js).call('f', 'http://yangkeduo.com/search_result.html?search_key=拉杆箱','rBTZeV9pkS+MZwBRTyx6Ag==')
# print(anti_content)

# ctx = execjs.compile(js)
# anti_content = ctx.call('result', 'http://yangkeduo.com/search_result.html?search_key=')
# # print(anti_content)
#
# a = '"goodsType":1,"localGroups":[],"hasLocalGroup":1,"bannerHeight":375,"topGallery":[{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F12076859-d614-4920-a675-1fa33f0666b4.jpeg","id":214600706508},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-07-09\u002Fec41ae0a-70d1-478f-aaf4-f9647618a58e.jpg","id":214600706507},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F9d66527d-e372-4419-b370-aac4e029435f.jpeg","id":214600706509},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F251a0ef1-38c2-496a-9fd3-a742d52dc6a1.jpeg","id":214600706510},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F69f8bd37-078f-4113-8dcb-a2d4ad59db64.jpeg","id":214600706511},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F1ebc04c5-5a02-40a0-88c7-f41a6a0189de.jpeg","id":214600706512},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fb008faba-68eb-4a70-885a-5ea61f0da3d4.jpeg","id":214600706513},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F957eeb09-8f3f-4fd7-a730-8924c01cde01.jpeg","id":214600706514},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fe5aa740c-c9db-4f04-b28f-ecc1fba74e48.jpeg","id":214600706515},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fgoods\u002Fimages\u002F2019-11-14\u002Feb10376a-dcd4-409d-862e-ce4e68a6567c.jpg","id":214600706516}],"viewImageData":["https:\u002F\u002Fimg.pddpic'
# import re
# import json
# b = re.findall('"topGallery":(\[.*?\])', a)[0]
# print(json.loads(b))


import requests

a = {'url': 'https://detail.tmall.com/item.htm?id=569676181813&ns=1&abbucket=17', 'title': '梦旅者铝框拉杆箱 超静音万向轮行李箱女旅行箱男小型皮箱20 22寸', 'original_price': '956.00-1296.00', 'promotion_price': '478.00-648.00', 'service': '正品保证,极速退款,退货运费险,七天无理由退换', 'reputation': '描述: 4.9 服务: 4.9 物流: 4.9', 'sale_count': 7500, 'favorite_count': 163027, 'detail_str': '产品参数：品牌:\xa0Dreamtraveller/梦旅者质地:\xa0PC闭合方式:\xa0锁扣图案:\xa0纯色风格:\xa0时尚潮流成色:\xa0全新尺寸:\xa020寸(德国工艺，原创设计)\xa022寸(德国工艺，原创设计)\xa024寸(德国工艺，原创设计)\xa026寸(德国工艺，原创设计)\xa028寸(德国工艺，原创设计)性别:\xa0男女通用颜色分类:\xa0L纹亚光白色\xa0L纹亚光黑色\xa0L纹亮面银色\xa0折叠纹亚光白色\xa0折叠纹亚光墨绿\xa0折叠纹沙漠玫瑰粉\xa0折叠纹亚光黑色\xa0折叠纹冰川蓝\xa0折叠纹波尔多红内部结构:\xa0拉链暗袋\xa0手机袋\xa0证件袋\xa0夹层拉链袋\xa0电脑插袋是否配包:\xa0否有无拉杆:\xa0有滚轮样式:\xa0万向轮上市时间:\xa02018年春夏货号:\xa01989里料材质:\xa0涤纶适用对象:\xa0青年箱包硬度:\xa0硬锁的类型:\xa0TSA密码锁是否带锁:\xa0是销售渠道类型:\xa0纯电商(只在线上销售)是否有扩展层:\xa0否', 'cover_url': 'https://img.alicdn.com//img.alicdn.com/imgextra/i2/2901218787/O1CN01WOKxFX2EmUs4pjCwG_!!0-item_pic.jpg', 'comment_count': 4044, 'impression': '外型好看(826)，质量好(778)，轮子滑行顺畅(303)，尺寸合适(298)，做工挺好(247)', 'site_from': 2, 'site_type': 1, 'price_range': '[459,750]'}
requests.post('http://127.0.0.1:8002/api/goods/save',data=a)


