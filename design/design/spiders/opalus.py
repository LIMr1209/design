import scrapy
from design.items import ProduceItem
import re
import requests
import hashlib
import random
import json


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


class DesignCaseSpider(scrapy.Spider):
    name = 'opalus'
    allowed_domains = ['opalus.taihuoniao.com', 'www.laisj.com']

    page = 1
    tag = '车'  # 手表 数据线 机器人 移动电源 水杯 搅拌机 耳机 音箱 灯 集成灶  净化器 车  支架  门禁  手环 冰箱 牙刷  扇
    content = translation(tag).replace(' ', '_')
    # start_urls = ['http://opalus.taihuoniao.com/produce/list?tag=%s&page=%s' % (tag, page)]
    start_urls = ['http://www.laisj.com/publics2/work/search?keyword=%s&list_rows=16&page=%s' % (tag, page)]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.EasyDlPipeline': 301,
        }

    }

    # def parse(self, response):
    #     detail_list = response.xpath('//div[@class="d_j"]/a/@href').extract()
    #     for i in detail_list:
    #         yield scrapy.Request('http://opalus.taihuoniao.com' + i, callback=self.parse_detail,dont_filter=True)
    #     page = response.xpath('//div[@class="pager-total"]/text()').extract()[0]
    #     page = int(re.findall(r'(\d+)', page)[0]) // 20 + 1
    #     if self.page < page:
    #         self.page += 1
    #         yield scrapy.Request(
    #             url='http://opalus.taihuoniao.com/produce/list?tag=%s&page=%s' % (self.tag, self.page),
    #             callback=self.parse, dont_filter=True)
    # def parse_detail(self, response):
    #     # print('页数', self.page)
    #     item = ProduceItem()
    #     img_urls = response.xpath('//div[@class="product"]/img/@src').extract()
    #     item['tag'] = self.content
    #     item['img_urls'] = img_urls
    #     yield item
    #
    def parse(self, response):
        detail_list = response.xpath('//div[@class="list-item"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.laisj.com' + i, callback=self.parse_detail, dont_filter=True)
        if detail_list:
            self.page += 1
            yield scrapy.Request(
                url='http://www.laisj.com/publics2/work/search?keyword=%s&list_rows=16&page=%s' % (self.tag, self.page),
                callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        # print('页数', self.page)
        item = ProduceItem()
        img_urls = response.xpath('//div[@class="content-other"]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('\\', '/')
        # print(img_urls)
        item['tag'] = self.content
        item['img_urls'] = img_urls
        yield item
