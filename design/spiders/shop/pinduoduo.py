import logging
import random
import re
from urllib.parse import urlencode
import json

import requests
import time

from pydispatch import dispatcher
from scrapy import signals
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
    name = 'pdd'
    allowed_domains = ['yangkeduo.com']
    # 商品信息API
    search_url = 'http://apiv3.yangkeduo.com/search?'
    # goods_url = 'http://opalus-dev.taihuoniao.com/api/goods/save'
    goods_url = 'https://opalus.d3ingo.com/api/goods/save'
    fail_url = []
    suc_count = 0
    page = 1
    max_page = 20
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'AccessToken': 'ZIKT77A7HUXB22YZFJWIQU5AGJCWL7OPX2QEH4MGR3VPT2CELPOQ1128855',
        'VerifyAuthToken': 'CeySBEX_UMoMjS7_F5b4Egf8edac2fb3f33ca9e'
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = ['电风扇', '美容器', '剃须刀', '电动牙刷']
        self.price_range = ''
        super(PddSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("http://yangkeduo.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error(self.key_words)
        logging.error(self.page)

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
            'item_ver': 'lzqq',
            'source': 'index',
            'search_met': 'history',
            'requery': '0',
            'list_id': list_id,
            'sort': 'default',
            'filter': '',
            'track_data': 'refer_page_id,10002_1600936236168_2wdje7q7ue;refer_search_met_pos,0',
            'q': self.key_words[0],
            'page': self.page,
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
            item_data['cover_url'] = item['item_data']['goods_model']['thumb_url']
            item_data['title'] = item['item_data']['goods_model']['goods_name']
            item_data['category'] = self.key_words[0]
            item_data['original_price'] = str(item['item_data']['goods_model']['normal_price'] / 100)
            item_data['promotion_price'] = str(item['item_data']['goods_model']['price'] / 100)
            item_data['out_number'] = item['item_data']['goods_model']['goods_id']
            item_data['price_range'] = self.price_range
            item_data['sale_count'] = item['item_data']['goods_model']['sales']
            item_data['site_from'] = 10
            item_data['site_type'] = 1
            # url = 'http://yangkeduo.com/{}'.format(item['item_data']['goods_model']['link_url'])
            item_data['url'] = 'http://yangkeduo.com/goods.html?goods_id=%s' % item['item_data']['goods_model'][
                'goods_id']
            items_list.append(item_data)
        yield scrapy.Request(items_list[0]['url'], meta={'usedSelenium': True, "items_list": items_list},
                             callback=self.parse_detail,
                             dont_filter=True)

    def parse_detail(self, response):
        choice = '1'
        try:
            verify_tag = WebDriverWait(self.browser, 1, 0.5).until(
                EC.presence_of_element_located(
                    (By.ID, 'intelVerify')
                )
            )
            if verify_tag.is_displayed:
                self.logger.error('发现滑块验证，请手动验证并确认验证结果')
                choice = input('请输入您的选择：1，通过 2. 未通过')
        except:
            pass
        if choice == "1":
            img_urls = []
            try:
                data = re.findall('"topGallery":(\[.*?\])', self.browser.page_source)[0]
                data = json.loads(data)
                for i in data:
                    img_urls.append(i['url'])
            except:
                img_ele = self.browser.find_elements_by_xpath('//li[contains(@class,"islider-html")]/img')
                for i in img_ele:
                    img_urls.append(i.get_attribute('src'))
            items_list = response.meta['items_list']
            item = items_list.pop(0)
            item['img_urls'] = ','.join(img_urls)
            service_list = self.browser.find_elements_by_xpath('//div[@class="fsI_SU5H"]/div')
            service_list = [i.text for i in service_list if i.text]
            item['service'] = ','.join(service_list)
            try:
                comment_text = self.browser.find_element_by_xpath('//div[@class="ccIhLMdm"]')
                comment_text = re.findall('商品评价\((.*)\)', comment_text.text)[0]
                index = comment_text.find('万')
                if index != -1:
                    item['comment_count'] = int(float(comment_text[:index]) * 10000)
                else:
                    comment_count = re.search('\d+', comment_text)
                    item['comment_count'] = int(comment_count.group())
            except:
                item['comment_count'] = 0
            detail_keys = self.browser.find_elements_by_xpath('//div[@class="_8rUS_gSm"]/div[1]')
            detail_values = self.browser.find_elements_by_xpath('//div[@class="_8rUS_gSm"]/div[2]')
            detail_dict = {}
            detail_str_list = []
            for i in range(len(detail_keys)):
                detail_str_list.append(detail_keys[i].text + ':' + detail_values[i].text)
                detail_dict[detail_keys[i].text] = detail_values[i].text
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
            time.sleep(random.randint(5, 8))
            if items_list:
                yield scrapy.Request(items_list[0]['url'], meta={'usedSelenium': True, "items_list": items_list},
                                     callback=self.parse_detail,
                                     dont_filter=True)
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
