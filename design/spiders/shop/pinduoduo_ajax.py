import logging
import random
import re
from urllib.parse import urlencode
import json

import requests
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from design.utils.antiContent_Js import js
import execjs
import scrapy
from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider


class PddSpider(SeleniumSpider):
    # 爬虫启动时间
    name = 'pdd_ajax'
    allowed_domains = ['yangkeduo.com']
    # 商品信息API
    search_url = 'http://apiv3.yangkeduo.com/search?'
    # goods_url = 'http://opalus-dev.taihuoniao.com/api/goods/save'
    goods_url = 'https://opalus.d3ingo.com/api/goods/save'
    detail_url = 'http://yangkeduo.com/proxy/api/api/oak/integration/render?pdduid=9575597704'
    fail_url = []
    suc_count = 0
    page = 1
    max_page = 20
    headers = {
        # 'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'AccessToken': 'JAYDMQVKKPWSHFFVFJDQG64XFQD6K27LIVK6PU2TPRPVYZ3CNVOQ1128855',
        'VerifyAuthToken': 'CeySBEX_UMoMjS7_F5b4Egf8edac2fb3f33ca9e',
        'Content-Type': 'application/json'
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        'HTTPERROR_ALLOWED_CODES': [400],
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = ['水壶', '台灯', '电风扇', '美容器', '剃须刀', '电动牙刷']
        self.price_range = ''
        super(PddSpider, self).__init__(*args, **kwargs)
        old_num = len(self.browser.window_handles)
        js = 'window.open("http://yangkeduo.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def start_requests(self):
        """
        请求搜索页
        """
        url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words[0]
        yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})

    def get_parameters(self, response):
        """
        获取参数：list_id, flip, anti_content
        """
        list_id = re.findall('"listID":"(.*?)"', response.text, re.S)[0]
        flip = re.findall('"flip":"(.*?)"', response.text, re.S)[0]
        ctx = execjs.compile(js)
        anti_content = ctx.call('result', response.url)

        self.data = {
            'gid': '',
            'source': 'index',
            'search_met': 'history',
            'requery': '0',
            'list_id': list_id,
            'sort': 'default',
            'filter': '',
            'track_data': 'refer_page_id,10002_1600936236168_2wdje7q7ue;refer_search_met_pos,0',
            'q': self.key_words[0],
            'page': 1,
            'size': '50',
            'flip': flip,
            'anti_content': anti_content,
            'pdduid': '9575597704'
        }
        yield scrapy.Request(url=self.search_url + urlencode(self.data),
                             headers=self.headers,
                             callback=self.parse_list,
                             dont_filter=True)

    def parse_list(self, response):
        """
        获取商品信息
        """
        items = json.loads(response.text)['items']
        items_list = []
        for item in items:
            item_data = TaobaoItem()
            item_data['cover_url'] = item['thumb_url']
            item_data['title'] = item['goods_name']
            item_data['category'] = self.key_words[0]
            item_data['original_price'] = str(item['normal_price'] / 100)
            item_data['promotion_price'] = str(item['price'] / 100)
            item_data['out_number'] = item['goods_id']
            item_data['price_range'] = self.price_range
            item_data['sale_count'] = item['sales']
            item_data['site_from'] = 10
            item_data['site_type'] = 1
            # url = 'http://yangkeduo.com/{}'.format(item['item_data']['goods_model']['link_url'])
            item_data['url'] = 'http://yangkeduo.com/goods.html?goods_id=%s' % item['goods_id']
            items_list.append(item_data)
        formdata = {"goods_id": items_list[0]['out_number']}
        yield scrapy.Request(self.detail_url, method='POST', meta={"items_list": items_list},
                             callback=self.parse_detail,
                             body=json.dumps(formdata), dont_filter=True, headers=self.headers)

    def parse_detail(self, response):
        items_list = response.meta['items_list']
        item = items_list.pop(0)
        detail_data = json.loads(response.text)
        img_urls = []
        item['original_price'] = str(detail_data['price']['min_on_sale_normal_price'])+'-'+str(detail_data['price']['max_on_sale_normal_price'])
        item['promotion_price'] = str(detail_data['price']['min_on_sale_group_price'])+'-'+str(detail_data['price']['max_on_sale_group_price'])
        item['img_urls'] = ','.join(img_urls)
        service_list = []
        for i in detail_data['service_promise']:
            service_list.append(i['type'])
        item['service'] = ','.join(service_list)
        item['comment_count'] = item['review']['review_num']
        detail_dict = {}
        detail_str_list = []
        for i in detail_data['goods']['goods_property']:
            detail_str_list.append(i['key'] + ':' + i['values'])
            detail_dict[i['key']] = i['values']
        item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
        item['detail_str'] = ', '.join(detail_str_list)
        good_data = dict(item)
        print(good_data)
        res = requests.post(url=self.goods_url, data=good_data)
        if res.status_code != 200 or json.loads(res.content)['code']:
            logging.error("产品保存失败" + good_data['url'])
            logging.error(json.loads(res.content)['message'])
            self.fail_url.append(good_data['url'])
        else:
            self.suc_count += 1
        time.sleep(2)
        if items_list:
            formdata = {"goods_id": items_list[0]['out_number']}
            yield scrapy.Request(self.detail_url, method='POST', meta={"items_list": items_list},
                                 callback=self.parse_detail,
                                 body=json.dumps(formdata), dont_filter=True, headers=self.headers)
        else:
            self.page += 1
            if self.page <= self.max_page:
                self.data['page'] = self.page
                yield scrapy.Request(url=self.search_url + urlencode(self.data),
                                     headers=self.headers,
                                     callback=self.parse_list,
                                     dont_filter=True)
            else:
                self.key_words.pop(0)
                self.page = 1
                url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words[0]
                yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})
