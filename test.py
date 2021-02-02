# coding:utf-8


# import execjs
# from design.utils.antiContent_Js import js
# #
# # with open('design/utils/anti_content_new.js', 'r', encoding='utf-8') as f:
# #     js = f.read()
# # anti_content = execjs.compile(js).call('f', 'http://yangkeduo.com/search_result.html?search_key=拉杆箱','rBTZeV9pkS+MZwBRTyx6Ag==')
# # print(anti_content)
#
# # ctx = execjs.compile(js)
# # anti_content = ctx.call('result', 'http://yangkeduo.com/search_result.html?search_key=')
# # # print(anti_content)
# #
# # a = '"goodsType":1,"localGroups":[],"hasLocalGroup":1,"bannerHeight":375,"topGallery":[{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F12076859-d614-4920-a675-1fa33f0666b4.jpeg","id":214600706508},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-07-09\u002Fec41ae0a-70d1-478f-aaf4-f9647618a58e.jpg","id":214600706507},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F9d66527d-e372-4419-b370-aac4e029435f.jpeg","id":214600706509},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F251a0ef1-38c2-496a-9fd3-a742d52dc6a1.jpeg","id":214600706510},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F69f8bd37-078f-4113-8dcb-a2d4ad59db64.jpeg","id":214600706511},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F1ebc04c5-5a02-40a0-88c7-f41a6a0189de.jpeg","id":214600706512},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fb008faba-68eb-4a70-885a-5ea61f0da3d4.jpeg","id":214600706513},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F957eeb09-8f3f-4fd7-a730-8924c01cde01.jpeg","id":214600706514},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fe5aa740c-c9db-4f04-b28f-ecc1fba74e48.jpeg","id":214600706515},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fgoods\u002Fimages\u002F2019-11-14\u002Feb10376a-dcd4-409d-862e-ce4e68a6567c.jpg","id":214600706516}],"viewImageData":["https:\u002F\u002Fimg.pddpic'
# # import re
# # import json
# # b = re.findall('"topGallery":(\[.*?\])', a)[0]
# # print(json.loads(b))
#
#
# import requests
# #
# # a = {'url': 'https://detail.tmall.com/item.htm?id=569676181813&ns=1&abbucket=17',
# #      'title': '梦旅者铝框拉杆箱 超静音万向轮行李箱女旅行箱男小型皮箱20 22寸', 'original_price': '956.00-1296.00',
# #      'promotion_price': '478.00-648.00', 'service': '正品保证,极速退款,退货运费险,七天无理由退换', 'reputation': '描述: 4.9 服务: 4.9 物流: 4.9',
# #      'sale_count': 7500, 'favorite_count': 163027,
# #      'detail_str': '产品参数：品牌:\xa0Dreamtraveller/梦旅者质地:\xa0PC闭合方式:\xa0锁扣图案:\xa0纯色风格:\xa0时尚潮流成色:\xa0全新尺寸:\xa020寸(德国工艺，原创设计)\xa022寸(德国工艺，原创设计)\xa024寸(德国工艺，原创设计)\xa026寸(德国工艺，原创设计)\xa028寸(德国工艺，原创设计)性别:\xa0男女通用颜色分类:\xa0L纹亚光白色\xa0L纹亚光黑色\xa0L纹亮面银色\xa0折叠纹亚光白色\xa0折叠纹亚光墨绿\xa0折叠纹沙漠玫瑰粉\xa0折叠纹亚光黑色\xa0折叠纹冰川蓝\xa0折叠纹波尔多红内部结构:\xa0拉链暗袋\xa0手机袋\xa0证件袋\xa0夹层拉链袋\xa0电脑插袋是否配包:\xa0否有无拉杆:\xa0有滚轮样式:\xa0万向轮上市时间:\xa02018年春夏货号:\xa01989里料材质:\xa0涤纶适用对象:\xa0青年箱包硬度:\xa0硬锁的类型:\xa0TSA密码锁是否带锁:\xa0是销售渠道类型:\xa0纯电商(只在线上销售)是否有扩展层:\xa0否',
# #      'cover_url': 'https://img.alicdn.com//img.alicdn.com/imgextra/i2/2901218787/O1CN01WOKxFX2EmUs4pjCwG_!!0-item_pic.jpg',
# #      'comment_count': 4044, 'impression': '外型好看(826)，质量好(778)，轮子滑行顺畅(303)，尺寸合适(298)，做工挺好(247)', 'site_from': 2,
# #      'site_type': 1, 'price_range': '[459,750]'}
# # requests.post('http://127.0.0.1:8002/api/goods/save', data=a)
# #
# # import requests
#
#
# #
# # proxies = {'http': 'http://tps125.kdlapi.com:15818'}
# # headers = {
# #      'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
# # }
# #
# # response = requests.get('http://dev.kdlapi.com/testproxy', proxies=proxies)
# # print(response.content)
#
# def chunks(l, n):
#     """Yield successive n-sized chunks from l."""
#     for i in range(0, len(l), n):
#         yield l[i:i + n]
#
# l = [1,2,3,4,5,6,7,8,9,10,11]
# n = 10000
#
# # print([l[i:i + n] for i in range(0, len(l), n)])
# # from scrapy.http import HtmlResponse
# #
# # import requests
# #
# # res = requests.get('https://opalus.d3ingo.com/')
# #
# #
# # html = HtmlResponse(url=res.url,
# #             body=res.content,
# #             request=res.request,
# #             # 最好根据网页的具体编码而定
# #             encoding='utf-8',
# #             status=200)
#
#
# import os
# # os.environ["EXECJS_RUNTIME"] = 'Node'
# print(execjs.get().name)
# ctx = execjs.compile(js)
# anti_content = ctx.call('result', 'http://yangkeduo.com/search_result.html?search_key=拉杆箱')
# print(anti_content )
import json

import requests

# from requests.exceptions import ProxyError
#
# porxy =  {'http': 'www.taihuoniao.com', 'https': 'www.taihuoniao.com:15818'}
# url = 'https://ip.cn/api/index?ip=&type=0'
# try:
#     res = requests.get(url, proxies=porxy)
# except requests.exceptions.RequestException as e:
#     print(e)
# except ProxyError as e:
#     print(e)
# # response = etree.HTML(res.content)
# # print(response.xpath('//*[@id="tab0_ip"]/text()'))
#
# data = json.loads(res.content)
# print(data)

# data_list = [{'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/24764/36/8363/94637/5c754466E5008e289/ab7bbe879a2d7314.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/10581/25/11920/75466/5c754467Edb597f62/c64abb35ece57b73.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '调动牙刷 飞利浦的非常好用，给女儿和朋友买了两支。质量好  刷的干净   非常喜欢', 'buyer': 'j***p', 'style': 'HX3216/01浅蓝色', 'date': '2019-02-26 21:51:35'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/23748/29/1028/94032/5c0e699bE1693a90f/6dcfc53aa811bce1.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/27388/20/1006/112842/5c0e699cEf3b04b75/ba992e69ae2fbc50.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/27195/8/1002/111064/5c0e699cE3cdcb792/02a5d40a22f733bf.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/6980/40/8516/117916/5c0e699dEcd02ac72/caace1e6ed6479f2.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '本人其实是第一次用电动牙刷，室友说飞利浦用的感觉不错所以我也来买，客服的服务很好很耐心，牙刷的握感很好，样式也很好看。\n收到货以后晚上我就使用了一下，感觉振动的速度和强度是第一次使用可以接受的，不会震得头疼或者不能忍受之类的，而且刷的也比普通牙刷要干净，区域提醒也很贴心。\n而且店家还送了四个刷头和一个旅行收纳盒，可以说是非常超值了！\n感觉可以一直用很久了。\n充电是那种接触式的也比较放心，机身都是防水的可以放心冲。\n很满意！！', 'buyer': '欧阳小番茄', 'style': 'HX3216/01浅蓝色', 'date': '2018-12-10 21:26:53'}, {'positive_review': 14364, 'comment_count': 28104, 'images': '', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '电动牙刷形状很好看，防水性强，刷头比较柔软，不会牙龈出血，会它刷牙感觉比手动的刷得干净得多', 'buyer': 'j***a', 'style': '去除牙菌斑智能护龈 男女通用HX3216', 'date': '2019-06-20 13:53:14'}, {'positive_review': 14364, 'comment_count': 28104, 'images': '', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '静音效果很好，洗得也很干净，很划算，而且物流很快，当天下单当天到货，值得购买', 'buyer': 'j***1', 'style': 'HX3216/01浅蓝色', 'date': '2018-06-30 22:34:51'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/77969/6/7058/223931/5d5120a7E77674dc6/022f268e8902f8b7.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/55929/39/7476/196846/5d5120a7E05f5a99f/4ac74f8870c1aecd.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/80406/7/7031/202152/5d5120a7E2d4d1b13/bfccf50be9773802.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '价格很便宜 注册之后再送刷头一只 声音也可以 用起来很方便 送盒子', 'buyer': '9***5', 'style': '去除牙菌斑智能护龈 男女通用HX3216', 'date': '2019-08-12 16:17:43'}, {'positive_review': 14364, 'comment_count': 28104, 'images': '', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '很精致的牙刷，手拿着很有质感舒服。刷头毛也不硬，功能和震动力度不错，清洁效果很棒。超级防水好用。', 'buyer': '维他命00000', 'style': '去除牙菌斑智能护龈 男女通用HX3216', 'date': '2019-08-03 10:49:09'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/45778/15/16331/367656/5dd9cbabE10659759/7380c1bb9c15a879.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '使用起来很舒服，电动的肯定刷起来更干净，快捷方便', 'buyer': '你***宁', 'style': '去除牙菌斑智能护龈 男女通用HX3216', 'date': '2019-11-24 08:15:39'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/11537/36/6505/89899/5c40709fE634549b3/773b16d6328d5ced.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/9040/22/13222/103486/5c4070a2E140185f9/eac2c6f79f8d0824.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/22367/3/5667/112562/5c4070a4E4e69c786/f59e0196e2bdcb36.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/14664/37/5666/90074/5c4070a6Ef37d9fbf/5d5c80db13e5c2f8.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/7522/15/12723/102874/5c4070a8E81444463/5108eeea105a86d6.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/7757/28/12965/97423/5c4070a9E16c83f0e/ec203732d9b2aae8.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '首先，快递非常快，两天不到就到了，京东的物流一向很给力。其次，包装很完整。\n收到货迫不及待打开了。感谢卖家送的四个刷头。一年都不用买了。试了下机子，声音不大。在接受范围内。颜色也是很简洁大方。总之，很满意的一次购物。一会用下感受感受。', 'buyer': 'v***泽', 'style': 'HX3216/01浅蓝色', 'date': '2019-01-17 20:10:18'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t26965/22/864742048/107028/e5f62182/5bbc1e97N6497b187.jpg,https://img30.360buyimg.com/shaidan/s616x405_jfs/t25357/2/1769158622/104994/cf253d8b/5bbc1e98N00ebad08.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '以前买过，质量很好，这次再买两把。做工细致，使用舒适，卖家发货很快，物流态度好。好评！', 'buyer': '打***8', 'style': 'HX3216/01浅蓝色', 'date': '2018-10-09 11:20:56'}, {'positive_review': 14364, 'comment_count': 28104, 'images': 'https://img30.360buyimg.com/shaidan/s616x405_jfs/t1/93076/1/8096/123119/5e021539E0f45abdf/e3e96156946312fe.jpg', 'love_count': 0, 'reply_count': 0, 'score': 5, 'type': 0, 'impression': '清洁能力强(33)  操作便捷(30)  方便省事(26)  使用舒适(18)  美观大气(16)  美观大方(12)  工艺精美(11)  耐用性佳(9)  声音很轻(7)  保护牙齿(6)  优质好用(2)  女士适用(2)  保修期长(1)  ', 'site_from': 11, 'good_url': 'https://item.jd.com/20623768031.html', 'first': '不错，质量很好，大牌子就是好，很稳定，比以前用的好', 'buyer': '李翔3758', 'style': '去除牙菌斑智能护龈 男女通用HX3216', 'date': '2019-12-24 21:40:09'}]
#
# res = requests.post('http://127.0.0.1:8002/api/comment/save',json=data_list, data={'good_url':1,'end':1},)
#
#
# print(type(res.json()))

s = requests.Session()
s.auth = ('user', 'pass')
s.headers.update({'x-test': 'true'})

# both 'x-test' and 'x-test2' are sent
res = s.get('http://httpbin.org/headers', headers={'x-test2': 'true'})

print(res.request.headers)
res.iter_content()

a = {
     '挂烫机': ['https://item.jd.com/100002401863.html', 'https://item.jd.com/100009117137.html',
             'https://item.jd.com/4502061.html', 'https://item.jd.com/10021981637445.html',
             'https://item.jd.com/6429477.html', 'https://item.jd.com/70028993318.html',
             'https://item.jd.com/100000076524.html', 'https://item.jd.com/57404627604.html',
             'https://item.jd.com/67611341556.html', 'https://item.jd.com/38512449004.html',
             'https://item.jd.com/10022734916159.html', 'https://item.jd.com/66035389662.html',
             'https://item.jd.com/49328943409.html', 'https://item.jd.com/49328943409.html',
             'https://item.jd.com/42286494284.html', 'https://item.jd.com/715472.html',
             'https://item.jd.com/65223166312.html', 'https://item.jd.com/68353820093.html',
             'https://item.jd.com/68952396894.html', 'https://item.jd.com/13183603374.html',
             'https://item.jd.com/10020078673342.html', 'https://item.jd.com/68862685518.html',
             'https://item.jd.com/49328943409.html', 'https://item.jd.com/10020078673342.html',
             'https://item.jd.com/68862685518.html', 'https://item.jd.com/49328943409.html',
             'https://item.jd.com/10025243004612.html', 'http://item.jd.com/3280109.html',
             'http://item.jd.com/1043580.html'],
     '烘衣机': ['https://item.jd.com/100003960176.html', 'https://item.jd.com/100004796479.html',
             'https://item.jd.com/11642672907.html', 'https://item.jd.com/100016056428.html',
             'https://item.jd.com/100001454118.html', 'https://item.jd.com/59736228459.html',
             'https://item.jd.com/10023063705058.html', 'https://item.jd.com/65157951640.html',
             'https://item.jd.com/31388538386.html',
             'https://item.jd.com/65970073462.html', 'https://item.jd.com/57266290878.html',
             'https://item.jd.com/100014734126.html', 'https://item.jd.com/10024944644041.html',
             'https://item.jd.com/100009166194.html', 'https://item.jd.com/10026094752041.html',
             'https://item.jd.com/100008918787.html', 'https://item.jd.com/23707799621.html',
             'https://item.jd.com/10022773456006.html', 'https://item.jd.com/1301066.html',
             'https://item.jd.com/53100971538.html', 'https://item.jd.com/100006744339.html',
             'https://item.jd.com/11331178020.html', 'https://item.jd.com/10026032190665.html',
             'https://item.jd.com/29157221900.html', 'https://item.jd.com/10023263243750.html',
             'https://item.jd.com/48022530867.html'],
     '烤箱': ['https://item.jd.com/2375700.html', 'https://item.jd.com/2375700.html', 'https://item.jd.com/2375700.html',
            'https://item.jd.com/2375700.html', 'https://item.jd.com/30267340200.html',
            'https://item.jd.com/2771999.html', 'https://item.jd.com/62012743827.html',
            'https://item.jd.com/30297737858.html', 'https://item.jd.com/100005801565.html',
            'https://item.jd.com/27861329807.html', 'https://item.jd.com/100005310232.html',
            'https://item.jd.com/57229799297.html', 'https://item.jd.com/34934393802.html',
            'https://item.jd.com/4665231.html', 'https://item.jd.com/10025448957258.html',
            'https://item.jd.com/71713979509.html', 'https://item.jd.com/100007539398.html',
            'https://item.jd.com/7076331.html', 'https://item.jd.com/10026004625891.html',
            'https://item.jd.com/10022029245907.html', 'https://item.jd.com/2375700.html',
            'https://item.jd.com/2375700.html', 'https://item.jd.com/40038346018.html',
            'https://item.jd.com/50895998242.html', 'https://item.jd.com/40038346018.html',
            'https://item.jd.com/50895998242.html', 'https://item.jd.com/50895998242.html',
            'https://item.jd.com/50895998242.html', 'https://item.jd.com/50895998242.html',
            'https://item.jd.com/50895998242.html']}
