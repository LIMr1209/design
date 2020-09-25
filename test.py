import execjs
from design.utils.antiContent_Js import js
#
# with open('design/utils/anti_content_new.js', 'r', encoding='utf-8') as f:
#     js = f.read()
# anti_content = execjs.compile(js).call('f', 'http://yangkeduo.com/search_result.html?search_key=拉杆箱','rBTZeV9pkS+MZwBRTyx6Ag==')
# print(anti_content)

ctx = execjs.compile(js)
anti_content = ctx.call('result', 'http://yangkeduo.com/search_result.html?search_key=')
# print(anti_content)

a = '"goodsType":1,"localGroups":[],"hasLocalGroup":1,"bannerHeight":375,"topGallery":[{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F12076859-d614-4920-a675-1fa33f0666b4.jpeg","id":214600706508},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-07-09\u002Fec41ae0a-70d1-478f-aaf4-f9647618a58e.jpg","id":214600706507},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F9d66527d-e372-4419-b370-aac4e029435f.jpeg","id":214600706509},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F251a0ef1-38c2-496a-9fd3-a742d52dc6a1.jpeg","id":214600706510},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F69f8bd37-078f-4113-8dcb-a2d4ad59db64.jpeg","id":214600706511},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F1ebc04c5-5a02-40a0-88c7-f41a6a0189de.jpeg","id":214600706512},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fb008faba-68eb-4a70-885a-5ea61f0da3d4.jpeg","id":214600706513},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002F957eeb09-8f3f-4fd7-a730-8924c01cde01.jpeg","id":214600706514},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fmms-material-img\u002F2020-06-10\u002Fe5aa740c-c9db-4f04-b28f-ecc1fba74e48.jpeg","id":214600706515},{"url":"https:\u002F\u002Fimg.pddpic.com\u002Fgoods\u002Fimages\u002F2019-11-14\u002Feb10376a-dcd4-409d-862e-ce4e68a6567c.jpg","id":214600706516}],"viewImageData":["https:\u002F\u002Fimg.pddpic'
import re
import json
b = re.findall('"topGallery":(\[.*?\])', a)[0]
print(json.loads(b))