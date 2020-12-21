import json
import random
import time, datetime
import requests
from fake_useragent import UserAgent

# comment_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
comment_url = 'https://opalus.d3ingo.com/api/comment/save'
comment_data_url = 'http://yangkeduo.com/proxy/api/reviews/%s/list?pdduid=9575597704&page=%s&size=20&enable_video=1&enable_group_review=1&label_id=0'
proxies = {'http': ''}


def comment_pdd_js(out_number):
    comment_page = 1
    while True:
        num = random.randint(5, 10)
        time.sleep(num)
        ua = UserAgent().random
        headers = {
            'Referer': 'http://yangkeduo.com/goods_comments.html?goods_id=%s' % out_number,
            'User-Agent': ua,
            'AccessToken': 'OSAR37W2Z26BM7JKEJAZMFDXNFNO3IKEMINREDOO3SEA7DITK7VQ1128855',
            'VerifyAuthToken': 'yiNF63KwVYtT3frnBC1Rvw9a0471827507f365b',
        }
        comment_res = requests.get(comment_data_url % (out_number, comment_page), headers=headers,
                                   proxies=proxies, verify=False)
        result = json.loads(comment_res.content)
        if 'empty_comment_text' not in result:
            print('被限制')
            print(out_number)
            break

        for i in result['data']:
            comment = {}
            try:
                if i['comprehensive_dsr'] < 3:
                    comment['type'] = 1
                elif i['comprehensive_dsr'] == 3:
                    comment['type'] = 2
                else:
                    comment['type'] = 0
            except:
                if i['desc_score'] < 3:
                    comment['type'] = 1
                elif i['desc_score'] == 3:
                    comment['type'] = 2
                else:
                    comment['type'] = 0
            comment['good_url'] = "http://yangkeduo.com/goods.html?goods_id=%s" % out_number
            if i['comment'] != "此用户未填写文字评论":
                comment['first'] = i['comment']
            if 'append' in i and i['append']:
                comment['add'] = i['append']['comment']
            comment['buyer'] = i['name']
            comment['site_from'] = 10
            if i['specs']:
                style = json.loads(i['specs'])
                if style:
                    style_str = style[0]['spec_key'] + ":" + style[0]['spec_value']
                    comment['style'] = style_str
            if i['time']:
                timeArray = time.localtime(i['time'])
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                comment['date'] = otherStyleTime
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
            comment['good_url'] = "http://yangkeduo.com/goods.html?goods_id=%s" % out_number
            try:
                res = requests.post(comment_url, data=comment)
            except Exception as e:
                time.sleep(3)
                res = requests.post(comment_url, data=comment)
            break
        comment_page += 1


import urllib3

urllib3.disable_warnings()
res = requests.get('https://opalus.d3ingo.com/api/good_comment?site_from=10&category=吹风机')
res = json.loads(res.content)
for i in res['data']:
    comment_pdd_js(str(i['number']))
