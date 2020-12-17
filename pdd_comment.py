import json
import time, datetime
import requests
from fake_useragent import UserAgent

# comment_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
comment_url = 'https://opalus.d3ingo.com/api/comment/save'
comment_data_url = 'http://yangkeduo.com/proxy/api/api/engels/reviews/sku/review/list?&goods_id=%s&page=%s&size=10&sku_id=0'
proxies = {'http': ''}


def comment_pdd_js(out_number):
    comment_page = 1
    while True:
        ua = UserAgent().random
        headers = {
            'Referer': 'http://yangkeduo.com/goods_comments.html?goods_id=%s' % out_number,
            'User-Agent': ua,
            'AccessToken': 'LNS3FWZT3NFTMA7TWYZJWGPQ6KL24ZZ6PYX4VZ7HRBOS6SYW6F5Q1128855'
        }
        comment_res = requests.get(comment_data_url % (out_number, comment_page), headers=headers,
                                   proxies=proxies, verify=False)
        result = json.loads(comment_res.content)
        for i in result['data']:
            comment = {}
            if i['comprehensive_dsr'] < 3:
                comment['type'] = 1
            elif i['comprehensive_dsr'] == 3:
                comment['type'] = 2
            else:
                comment['type'] = 0
            comment['good_url'] = "http://yangkeduo.com/goods.html?goods_id=%s"%out_number
            comment['first'] = i['comment']
            comment['add'] = i['append']['content'] if i['append'] else ''
            comment['buyer'] = i['name']
            comment['site_from'] = 10
            if i['specs']:
                style = json.loads(i['specs'])[0]
                style_str = style['spec_key'] +":"+ style['spec_value']
                comment['style'] = style_str
            if i['time']:
                timeArray = time.localtime(i['time'])
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                comment['date'] =otherStyleTime
            try:
                res = requests.post(comment_url, data=comment)
            except Exception as e:
                time.sleep(3)
                res = requests.post(comment_url, data=comment)
            if res.status_code != 200 or json.loads(res.content)['code']:
                print(json.loads(res.content)['message'])

        if not result['data']:
            comment = {}
            comment['end'] = 1
            comment['good_url'] = "http://yangkeduo.com/goods.html?goods_id=%s"%out_number
            try:
                res = requests.post(comment_url, data=comment)
            except Exception as e:
                time.sleep(3)
                res = requests.post(comment_url, data=comment)
            break
        comment_page += 1

res = requests.get('https://opalus.d3ingo.com/api/good_comment?site_from=10&category=吹风机')
res = json.loads(res.content)
for i in res['data']:
    comment_pdd_js(str(i['number']))