# import requests
# import re
# import json
# res = requests.get('https://rate.tmall.com/listTagClouds.htm?itemId=41305294954&isAll=true&isInner=true&t=1603103889422&groupId=&_ksTS=1603103889423_500&callback=jsonp501',stream=True)
# rex = re.compile('({.*})')
# result = json.loads(rex.findall(res.content.decode('utf-8'))[0])
# print(result)
# headers = {
#     'Referer': 'https://detail.tmall.com/item.htm?spm=a230r.1.14.9.622c2cd4YDRxx2&id=578865342527&ns=1&abbucket=6',
# }
# res = requests.get(
#     'https://rate.tmall.com/list_detail_rate.htm?order=3&append=0&content=1&groupId=&needFold=0&itemId=578865342527&spuId=1296479913&sellerId=1726473375&currentPage=2&tagId=&posi=&picture=&_ksTS=1603094362808_721&callback=jsonp722',
#     headers=headers)
# rex = re.compile('({.*})')
# result = json.loads(rex.findall(res.content.decode('utf-8'))[0])
# print(result['rateDetail']['rateList'])
# print(len(result['rateDetail']['rateList']))
# print(result['rateDetail']['paginator']['lastPage'])

import requests

res = requests.get("https://www.red-dot.org/search?tx_solr[filter][0]=result_type:online_exhibition&tx_solr[filter][1]=online_exhibition_type:Product Design&tx_solr[filter][3]=year:2020")
print(res.status_code)