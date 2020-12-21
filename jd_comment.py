import json
import random
import re
import time
from requests.adapters import HTTPAdapter
import requests
from fake_useragent import UserAgent

comment_url = 'https://opalus.d3ingo.com/api/comment/save'
# comment_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
# comment_url = 'https://opalus.d3ingo.com/api/comment/save'
# comment_data_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
# 当前sku 评论
comment_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
proxies = {'http': ''}


def comment_jd_js(out_number):
    comment_page = 0
    while True:
        num = random.randint(5, 10)
        time.sleep(num)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.jd.com/%s.html'%out_number,
            # 'User-Agent': ua,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Cookie': 'JSESSIONID=046620E1D8BC6E9E973E8C7BFC57A6D3.s1; Path=/',
        }
        url = comment_data_url % (out_number,comment_page)

        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        s.mount('https://', HTTPAdapter(max_retries=5))

        try:
            comment_res = s.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
        except requests.exceptions.RequestException as e:
            print('被限制')
            print(out_number)
            break

        # 54 好评 3 2 中评 1 差评
        rex = re.compile('({.*})')
        try:
            result = json.loads(rex.findall(comment_res.text)[0])
        except:
            print('被限制')
            print(out_number)
            break
        for i in result['comments']:
            comment = {}
            comment['positive_review'] = result['productCommentSummary']['goodCount']
            comment['comment_count'] = result['productCommentSummary']['commentCount']
            impression = ''
            for j in result['hotCommentTagStatistics']:
                impression += j['name'] + '(' + str(j['count']) + ')  '
            if i['score'] in [4,5]:
                comment['type'] = 0
            elif i['score'] in [3,2]:
                comment['type'] = 2
            elif i['score'] in [1]:
                comment['type'] = 1
            comment['impression'] = impression
            comment['site_from'] = 11
            comment['good_url'] = headers['Referer']
            if i['content'] == '此用户没有填写评论!':
                comment['first'] = ''
            elif i['content'] == '评价方未及时做出评价,系统默认好评!':
                comment['first'] = ''
            else:
                comment['first'] = i['content']
            if 'afterUserComment' in i and i['afterUserComment']:
                comment['add'] = i['afterUserComment']['content']
            comment['buyer'] = i['nickname']
            comment['style'] = i['productColor'] if 'productColor' in i else ''
            comment['date'] = i['creationTime']
            try:
                res = requests.post(comment_url, data=comment)
            except:
                time.sleep(3)
                res = requests.post(comment_url, data=comment)
            if res.status_code != 200 or json.loads(res.content)['code']:
                print(json.loads(res.content)['message'])

        pages = result['maxPage']
        if comment_page >= pages or not result['comments']:
            comment = {}
            comment['end'] = 1
            comment['good_url'] = headers['Referer']
            try:
                res = requests.post(comment_url, data=comment)
            except:
                time.sleep(3)
                res = requests.post(comment_url, data=comment)
            break
        comment_page += 1
import urllib3
urllib3.disable_warnings()
res = requests.get('https://opalus.d3ingo.com/api/good_comment?site_from=11&category=吹风机')
res = json.loads(res.content)
for i in res['data']:
    comment_jd_js(str(i['number']))