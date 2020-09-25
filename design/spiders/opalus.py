# import scrapy
# from design.items import ProduceItem
# import re
# import requests
# import hashlib
# import random
# import json
#
#
# # def translation(content):
# #     appid = '20190103000254181'
# #     secretKey = 'CfedDqlZBm2tG8nmQbnw'
# #     myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
# #     q = content
# #     fromLang = 'zh'
# #     toLang = 'en'
# #     salt = random.randint(32768, 65536)
# #     sign = appid + q + str(salt) + secretKey
# #     m1 = hashlib.md5()
# #     m1.update(sign.encode('utf-8'))
# #     sign = m1.hexdigest()
# #     params = {
# #         'appid': appid,
# #         'q': q,
# #         'from': fromLang,
# #         'to': toLang,
# #         'salt': str(salt),
# #         'sign': sign
# #     }
# #     response = requests.get(myurl, params=params)
# #     result = json.loads(response.text)
# #     return result['trans_result'][0]['dst']
#
#
# class ImageSpider(scrapy.Spider):
#     name = 'opalus_image'
#     allowed_domains = ['opalus.taihuoniao.com', 'www.laisj.com']
#
#     page = 1
#     tag = '扫地机器人'  # 手表 数据线 机器人 移动电源 水杯 搅拌机 耳机 音箱 灯 集成灶  净化器 车  支架  门禁  手环 冰箱 牙刷  扇
#     content = translation(tag).replace(' ', '_')
#
#     cookie = {'Hm_lvt_a6fa7c04b9ccd632817643f9ac3e41de': '1548401930',
#               '_ga': 'GA1.2.1357785688.1548401931',
#               'session': 'eyJjc3JmX3Rva2VuIjoiOGQ5MGIxNmVlZWMxZWMzOTRiYTIyODA4YzE5ODdjNjUyYmY1NGRjMSIsInRva2VuIjoicE5OeTg1R3NzUGRjZ1J3eSIsInVpZCI6MTJ9.D0QPcQ.BPxrLko4TGKs4zmRUHdeXAW8Vqk'
#               }
#     custom_settings = {
#         # 'LOG_LEVEL': 'INFO',
#         'DOWNLOAD_DELAY': 0,
#         'COOKIES_ENABLED': False,  # enabled by default
#         'ITEM_PIPELINES': {
#             'design.pipelines.EasyDlPipeline': 301,
#         }
#
#     }
#
#     def start_requests(self):
#         yield scrapy.Request(
#             url='http://opalus.taihuoniao.com/admin/image/list?page=%s&q=&t=1&prize_id=0&site_mark=www_baidu_robot&kind=0&status=0&deleted=0' % (
#                 self.page), cookies=self.cookie)
#
#     def parse(self, response):
#         item = ProduceItem()
#         img_urls = response.xpath('//tr[@id]/td[2]/a/img/@src').extract()
#         for i in range(len(img_urls)):
#             img_urls[i] = img_urls[i].replace('\\', '/')
#         item['tag'] = self.tag
#         item['img_urls'] = img_urls
#         yield item
#         print(item)
#         if self.page < 11:
#             self.page += 1
#             yield scrapy.Request(
#                 'http://opalus.taihuoniao.com/admin/image/list?page=%s&q=&t=1&prize_id=0&site_mark=www_baidu_robot&kind=0&status=0&deleted=0' % (
#                     self.page), cookies=self.cookie)
#
#
# class DesignCaseSpider(scrapy.Spider):
#     name = 'opalus_produce'
#     allowed_domains = ['opalus.taihuoniao.com', 'www.laisj.com']
#
#     page = 1
#     tag = '扫地机器人'  # 手表 数据线 机器人 移动电源 水杯 搅拌机 耳机 音箱 灯 集成灶  净化器 车  支架  门禁  手环 冰箱 牙刷  扇
#     content = translation(tag).replace(' ', '_')
#     start_urls = ['http://opalus.taihuoniao.com/produce/list?tag=%s&page=%s' % (tag, page)]
#
#     custom_settings = {
#         # 'LOG_LEVEL': 'INFO',
#         'DOWNLOAD_DELAY': 0,
#         'COOKIES_ENABLED': False,  # enabled by default
#         'ITEM_PIPELINES': {
#             'design.pipelines.EasyDlPipeline': 301,
#         }
#
#     }
#
#     def parse(self, response):
#         detail_list = response.xpath('//div[@class="d_j"]/a/@href').extract()
#         for i in detail_list:
#             yield scrapy.Request('http://opalus.taihuoniao.com' + i, callback=self.parse_detail, dont_filter=True)
#         page = response.xpath('//div[@class="pager-total"]/text()').extract()[0]
#         page = int(re.findall(r'(\d+)', page)[0]) // 20 + 1
#         if self.page < page:
#             self.page += 1
#             yield scrapy.Request(
#                 url='http://opalus.taihuoniao.com/produce/list?tag=%s&page=%s' % (self.tag, self.page),
#                 callback=self.parse, dont_filter=True)
#
#     def parse_detail(self, response):
#         # print('页数', self.page)
#         item = ProduceItem()
#         img_urls = response.xpath('//div[@class="product"]/img/@src').extract()
#         for i in range(len(img_urls)):
#             img_urls[i] = img_urls[i].replace('\\', '/')
#         item['tag'] = self.tag
#         item['img_urls'] = img_urls
#         yield item
