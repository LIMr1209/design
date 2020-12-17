import json
import re
import time

import requests
from fake_useragent import UserAgent

comment_url = 'https://opalus.d3ingo.com/api/comment/save'
# comment_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
# comment_url = 'https://opalus.d3ingo.com/api/comment/save'
comment_data_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
proxies = {'http': ''}


def comment_jd_js(out_number):
    comment_page = 0
    while True:
        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.jd.com/%s.html'%out_number,
            # 'User-Agent': ua,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Cache-Control': 'no-cache',
            # 'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=068CE69BEB8E77E7FF7D415202926236.s1; Path=/',
            # 'Host': 'club.jd.com',
            # 'Pragma': 'no-cache',
            # 'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            # 'sec-ch-ua-mobile': '?0',
            # 'Sec-Fetch-Dest': 'document',
            # 'Sec-Fetch-Mode': 'navigate',
            # 'Sec-Fetch-Site': 'none',
            # 'Sec-Fetch-User': '?1',
            # 'Upgrade-Insecure-Requests': '1',
        }
        url = comment_data_url % (out_number,comment_page)
        comment_res = requests.get(url, headers=headers,
                                   proxies=proxies, verify=False)

        # 54 好评 3 2 中评 1 差评
        rex = re.compile('({.*})')
        result = json.loads(rex.findall(comment_res.text)[0])
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
            comment['style'] = i['productColor']
            comment['date'] = i['creationTime']
            # try:
            #     res = requests.post(comment_url, data=comment)
            # except:
            #     time.sleep(3)
            #     res = requests.post(comment_url, data=comment)
            # if res.status_code != 200 or json.loads(res.content)['code']:
            #     print(json.loads(res.content)['message'])

        pages = result['maxPage']
        if comment_page >= pages or not result['maxPage']:
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

comment_jd_js(70645352770)
# res = requests.get('http://opalus-dev.taihuoniao.com/api/good_comment?site_from=10&category=吹风机')
# res = json.loads(res.content)
# for i in res['data']:
#     comment_jd_js(str(i['number']))