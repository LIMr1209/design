from urllib import parse
import requests
from pymongo import MongoClient

goods_url = 'https://opalus.d3ingo.com/api/goods/save'

mc = MongoClient("127.0.0.1", 27017)
test_db = mc["test"]

data = test_db.taobao.find({'is_suc': 1})
for i in data:
    itemId = parse.parse_qs(parse.urlparse('https:'+i['link']).query)['id'][0]
    url = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
    good = {}
    good['url'] = url
    good['price_range'] = i['price_range']
    res = requests.post(url=goods_url, data=good)