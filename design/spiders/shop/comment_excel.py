import json
import os
import random
import re
import time
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
import pandas as pd

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=5))  # 重试次数
s.mount('https://', HTTPAdapter(max_retries=5))


def save_excel(out_number,csv_data):
    n = 10000
    data_list = ([csv_data[i:i + n] for i in range(0, len(csv_data), n)])
    for i, j in enumerate(data_list):
        file_path = '{}.xlsx'.format(out_number)
        if not os.path.exists(file_path):
            df = pd.DataFrame(
                columns=['页面网址','买家','初评', '追评', '样式', '日期', '评分', '图片','点赞','回复'])
            df.to_excel(file_path, index=False)
        df = pd.read_excel(file_path, header=None)
        ds = pd.DataFrame(j)
        df = df.append(ds, ignore_index=True)
        df.to_excel(file_path, index=False, header=False)

def spider_comment(out_number, comment_page):
    suc_count = 0
    while True:
        comment_res = ''
        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.jd.com/%s.html' % out_number,
            # 'User-Agent': ua,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Cookie': '__jdv=76161171|direct|-|none|-|1608255795687; areaId=1; PCSYCityID=CN_110000_110100_110105; shshshfpa=1ea06a98-4acf-4194-8612-1f53aa095576-1608255797; shshshfpb=ptjkzrtRv%2FGXDRxvbTmMhXQ%3D%3D; ipLoc-djd=1-72-55653-0; jwotest_product=99; __jdu=16082557956851132232680; __jda=122270672.16082557956851132232680.1608255796.1608528276.1608546540.6; __jdc=122270672; shshshfp=e617994739299fc7d65b757f312bf7d1; 3AB9D23F7A4B3C9B=E7MDYEC5EOP32SWZP4FX4FOIZPNTF5NSHBOUS3IOKPFAUDJLD5FWSZSRWQUHEH5UA3DNBXQEWWVPPHK4LXTIDWNONE; shshshsID=fc4275835fb93217e88bce5600d92c29_5_1608547125459; __jdb=122270672.5.16082557956851132232680|6.1608546540; JSESSIONID=02182E6AC1F7B1F35FA6123414378436.s1',
        }
        # if comment_res:
        #     headers['Cookie'] = comment_res.headers.get('set-cookie')[1]
        url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'

        try:
            comment_res = s.get(url%(out_number, comment_page), headers=headers, verify=False, timeout=10)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}

        # 54 好评 3 2 中评 1 差评
        rex = re.compile('({.*})')
        try:
            result = json.loads(rex.findall(comment_res.text)[0])
        except:
            return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
        comments = []
        for i in result['comments']:
            # ['页面网址','大家印象','买家','初评', '追评', '样式', '日期', '评分', '图片','点赞','回复']
            img_urls = []
            if 'images' in i:
                for j in i['images']:
                    img_urls.append('https:'+j['imgUrl'].replace('s128x96_jfs','s616x405_jfs'))
            img_urls = '\n'.join(img_urls)
            comments.append(
                [
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(headers['Referer'])),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['nickname'] if i['nickname'] else '')),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['content'] if i['content'] else '')),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['afterUserComment']['content'] if 'afterUserComment' in i and i['afterUserComment'] else '')),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['productColor'] if 'productColor' in i else '')),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['creationTime'])),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['score'])),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(img_urls)),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['usefulVoteCount'])),
                    ILLEGAL_CHARACTERS_RE.sub(r'', str(i['replyCount'])),
                ]
            )
        save_excel(out_number,comments)
        print('写入成功,{},{}'.format(out_number, comment_page))
        suc_count += len(comments)
        pages = result['maxPage']
        if comment_page >= pages or not result['comments'] or suc_count > 5000:
            return {'success': True, 'message': "爬取完成", 'out_number': out_number}
        num = random.randint(3, 5)
        time.sleep(num)
        comment_page += 1

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings()
    # '7250818'
    for i in ['7250818']:
        print(spider_comment(i,0))