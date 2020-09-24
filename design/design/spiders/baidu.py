# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import random
import hashlib
from design.items import ProduceItem
import requests
import json
import re


def baidtu_uncomplie(url):
    res = ''
    c = ['_z2C$q', '_z&e3B', 'AzdH3F']
    d = {'w': 'a', 'k': 'b', 'v': 'c', '1': 'd', 'j': 'e', 'u': 'f', '2': 'g', 'i': 'h', 't': 'i', '3': 'j', 'h': 'k',
         's': 'l', '4': 'm', 'g': 'n', '5': 'o', 'r': 'p', 'q': 'q', '6': 'r', 'f': 's', 'p': 't', '7': 'u', 'e': 'v',
         'o': 'w', '8': '1', 'd': '2', 'n': '3', '9': '4', 'c': '5', 'm': '6', '0': '7', 'b': '8', 'l': '9', 'a': '0',
         '_z2C$q': ':', '_z&e3B': '.', 'AzdH3F': '/'}
    if (url == None or 'http' in url):
        return url
    else:
        j = url
        for m in c:
            j = j.replace(m, d[m])
        for char in j:
            if re.match('^[a-w\d]+$', char):
                char = d[char]
            res = res + char
        return res


def translation(content):
    appid = '20190103000254181'
    secretKey = 'CfedDqlZBm2tG8nmQbnw'
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    q = content
    fromLang = 'zh'
    toLang = 'en'
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    params = {
        'appid': appid,
        'q': q,
        'from': fromLang,
        'to': toLang,
        'salt': str(salt),
        'sign': sign
    }
    response = requests.get(myurl, params=params)
    result = json.loads(response.text)
    return result['trans_result'][0]['dst']


class BaiduImagesSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['http:image.baidu.com']
    start_urls = ['http://image.baidu.com/']
    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 301,
        }

    }
    base_url = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&' \
               'is=&fp=result&queryWord={0}&cl=2&lm =-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=&hd=&latest=&copyright=' \
               '&word={0}&s=&se=&tab=&width=&height=&face=0&' \
               'istype=2&qc=&nc=1&fr=&expermode=&force=&' \
               'pn={1}&rn=30&gsm=1e&'
    page = 30
    key_words = '台灯'
    # tag = translation(key_words).replace(' ', '_')


    def parse(self, response):
        headers = {'Referer': 'http://image.baidu.com/', 'Host': 'image.baidu.com'}
        url = self.base_url.format(self.key_words, str(self.page))
        yield Request(url, callback=self.get_pic,
                      dont_filter=True, headers=headers)

    def get_pic(self, response):
        headers = {'Referer': 'http://image.baidu.com/', 'Host': 'image.baidu.com'}
        item = ProduceItem()
        try:
            item['channel'] = 'baidu'
            response_json = response.text
            response_json = json.loads(response_json)
            response_data = response_json['data']
            if len(response_data) == 0:
                return
            for content in response_data:
                if content.get('thumbURL', None):
                    item['tag'] = self.key_words
                    item['img_url'] = baidtu_uncomplie(content['objURL'])
                    yield item
            self.page += 30
            if self.page > 15000:
                return
            next_url = self.base_url.format(self.key_words, str(self.page))
            yield Request(next_url, callback=self.get_pic,
                          dont_filter=True, headers=headers)
        except:
            return
