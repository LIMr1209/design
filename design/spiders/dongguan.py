# -*- coding: utf-8 -*-
import scrapy
from design.items import DesignItem

# 东莞杯国际工业设计大奖
data = {
    'channel': 'dgawards',
    'name': '',
    'color_tags': [],
    'brand_tags': [],
    'material_tags': [],
    'style_tags': [],
    'technique_tags': [],
    'other_tags': [],
    'user_id': 0,
    'kind': 1,
    'brand_id': 0,
    'prize_id': 21,
    'prize': '东莞杯国际工业设计大奖',
    'evt': 3,
    'prize_level': '',
    'category_id': 0,
    'status': 1,  # 状态
    'deleted': 0,  # 是否软删除
    'info': '',
}

year_url = {
    '2018': 'http://www.dgawards.com/',
    '2017': 'http://2017.dgawards.com/',
    '2016-2010': 'http://www.dgdesign.org.cn/2016/',
    '2013': 'http://www.dgdesign.org.cn/'
}

# 2017,2018 176条
# class DesignCaseSpider(scrapy.Spider):
#     name = 'dongguan'
#     allowed_domains = ['www.dgawards.com']
#     year = 2018
#     # year = 2017
#     id = 1
#     page = 1
#     url = 'http://www.dgawards.com/work/?id='
#     # url = 'http://2017.dgawards.com/work/?id='
#     start_urls = [url + str(id)]
#
#     def parse(self, response):
#         design_list = response.xpath('//div[@class="work_list"]/a/@href').extract()
#         print(response.url)
#         for design in design_list:
#             if self.year == 2018:
#                 yield scrapy.Request(url='http://www.dgawards.com/work/' + design, callback=self.parse_detail,
#                                      meta={'id': self.id}, dont_filter=True)
#             elif self.year == 2017:
#                 yield scrapy.Request(url='http://2017.dgawards.com/work/' + design, callback=self.parse_detail,
#                                      meta={'id': self.id}, dont_filter=True)
#         if self.page < 4:
#             self.page += 1
#             yield scrapy.Request(self.url + str(self.id) + '&page=' + str(self.page), callback=self.parse,
#                                  dont_filter=True)
#         if self.page == 4:
#             if self.id < 2:
#                 self.id += 1
#                 self.page = 1
#                 yield scrapy.Request(self.url + str(self.id), callback=self.parse, dont_filter=True)
#
#     def parse_detail(self, response):
#         # print(response.url)
#         item = DesignItem()
#         id = response.meta['id']
#         img_url = ''
#         if self.year == 2018:
#             img_url = response.xpath('//div[@class="work_cover"]/img/@src').extract()[0]
#             if not img_url.startswith('http://www.dgawards.com'):
#                 img_url = 'http://www.dgawards.com' + img_url
#         elif self.year == 2017:
#             img_url = response.xpath('//div[@class="work_cover"]/img/@src').extract()[0]
#             if img_url == 'fFBwciWTNNjCLShJanZ':
#                 return
#             if not img_url.startswith('http://2017.dgawards.com'):
#                 img_url = 'http://2017.dgawards.com' + img_url
#         title = response.xpath('//div[@class="detail_info"]/div[3]/span[2]/text()').extract()[0][5:]
#         prize_time = str(self.year)
#         try:
#             remark = response.xpath(
#                 '//div[@class="detail_info"]/div[3]/div/p/text() | //div[@class="detail_info"]/div[3]/div/p//span/text()').extract()[
#                 0]
#         except:
#             remark = ''
#         company = ''
#         designer = ''
#         tags = []
#         if id == 1:
#             tags = ['产品组']
#             company = response.xpath('//div[@class="detail_info"]/div[3]/span[1]/text()').extract()[0][5:]
#             designer = ''
#         elif id == 2:
#             designer = response.xpath('//div[@class="detail_info"]/div[3]/span[1]/text()').extract()[0][6:]
#             tags = ['概念组']
#             company = ''
#         item['img_url'] = img_url.strip()
#         item['title'] = title.strip()
#         item['company'] = company.strip()
#         item['prize_time'] = prize_time
#         item['remark'] = remark.strip()
#         item['tags'] = tags
#         item['designer'] = designer.strip()
#         for key, value in data.items():
#             item[key] = value
#         yield item

import re

a = {}


# 2012,2014,  1147条
# class DesignCaseSpider(scrapy.Spider):
#     name = 'dongguan'
#     allowed_domains = ['www.dgawards.com']
#     year = 2014  # 2014,2012
#     page = 1
#     url = 'http://www.dgdesign.org.cn/'
#     start_urls = [url + str(year) + '/']
#
#     def parse(self, response):
#         design_list = response.xpath('//div[@class="update"]//a/@href').extract()
#
#         for design in design_list:
#             yield scrapy.Request(url='http://www.dgdesign.org.cn/' + str(self.year) + '/' + design,
#                                  callback=self.parse_detail,
#                                  dont_filter=True)
#         page = response.xpath('//div[@class="scott"]/*[3]/text()').extract()[0]
#         if self.page < int(page):
#             self.page += 1
#             url = self.url + str(self.year) + '/?page=' + str(self.page)
#             print(url)
#             yield scrapy.Request(self.url + str(self.year) + '/?page=' + str(self.page), callback=self.parse,
#                                  dont_filter=True)
#         if self.page == int(page):
#             if self.year > 2013:
#                 self.year -= 2
#                 self.page = 1
#                 yield scrapy.Request(self.url + str(self.year) + '/', callback=self.parse,
#                                      dont_filter=True)
#
#     def parse_detail(self, response):
#         item = DesignItem()
#         img_url = response.xpath('//div[@id="works_list"]//a[1]/img/@src').extract()[0]
#
#         if not img_url.startswith('http://www.dgdesign.org.cn'):
#             img_url = 'http://www.dgdesign.org.cn' + img_url[2:]
#         message = response.xpath('//div[@id="works_list"]//td[2]//div[1]/span/text()').extract()
#         remark = ''
#         item['img_url'] = img_url.strip()
#         item['title'] = message[0].strip()
#         try:
#             item['company'] = message[4].strip()
#         except:
#             item['company'] = ''
#         item['prize_time'] = str(self.year)
#         item['remark'] = remark
#         item['tags'] = [message[1]]
#         item['designer'] = message[3].strip()
#         for key, value in data.items():
#             item[key] = value
#
#         yield item


# 2013  316条
#
# class DesignCaseSpider(scrapy.Spider):
#     name = 'dongguan'
#     allowed_domains = ['www.dgawards.com']
#     year = 2013
#     page = 1
#     start_urls = ['http://www.dgdesign.org.cn/work/']  # 2013
#
#     def parse(self, response):
#         design_list = response.xpath('//div[@class="update"]//a/@href').extract()
#         for design in design_list:
#             yield scrapy.Request(url='http://www.dgdesign.org.cn/work/' + design,
#                                  callback=self.parse_detail, dont_filter=True)
#         page = response.xpath('//div[@class="scott"]/*[3]/text()').extract()[0]
#         if self.page < int(page):
#             self.page += 1
#             yield scrapy.Request('http://www.dgdesign.org.cn/work/?page=' + str(self.page), callback=self.parse,
#                                  dont_filter=True)
#
#     def parse_detail(self, response):
#         item = DesignItem()
#         img_url = response.xpath('//div[@id="works_list"]//a[1]/img/@src').extract()[0]
#
#         if not img_url.startswith('http://www.dgdesign.org.cn'):
#             img_url = 'http://www.dgdesign.org.cn' + img_url[2:]
#         message = response.xpath('//div[@id="works_list"]//td[2]//div[1]/span/text()').extract()
#         remark = ''
#         item['img_url'] = img_url.strip()
#         item['title'] = message[0].strip()
#         try:
#             item['company'] = message[4].strip()
#         except:
#             item['company'] = ''
#         item['prize_time'] = str(self.year)
#         item['remark'] = remark
#         item['tags'] = [message[1]]
#         item['designer'] = message[3].strip()
#         for key, value in data.items():
#             item[key] = value
#         yield item
# 2015,2016,  813 条
class DesignCaseSpider(scrapy.Spider):
    name = 'dongguan'
    allowed_domains = ['www.dgawards.com']
    year = 2016
    # year = 2015
    page = 1
    typeid = 40  # 40 41 42 2016
    # typeid = 37  # 37 38 39 2015
    url = 'http://www.dgdesign.org.cn/'
    start_urls = [url + str(year) + '/?typeid=' + str(typeid)]

    def parse(self, response):
        design_list = response.xpath('//div[@class="update"]//a/@href').extract()
        for design in design_list:
            yield scrapy.Request(url='http://www.dgdesign.org.cn/' + str(self.year) + '/' + design,
                                 callback=self.parse_detail, meta={"page": self.page, 'typeid': self.typeid},
                                 dont_filter=True)
        page = response.xpath('//div[@class="scott"]/*[3]/text()').extract()[0]

        if self.page < int(page):
            self.page += 1
            url = self.url + str(self.year) + '/?typeid='+str(self.typeid)+ '&page=' + str(self.page)
            print(url)
            yield scrapy.Request(url, callback=self.parse,
                                 dont_filter=True)
        #
        if self.page == int(page):
            if self.typeid < 42: # 2016
            # if self.typeid < 39:
                self.typeid += 1
                yield scrapy.Request(url=self.url+str(self.year) + '/?typeid='+str(self.typeid), callback=self.parse,
                                     dont_filter=True)


    def parse_detail(self, response):
        item = DesignItem()
        # id = re.compile('\?id=\w+').search(response.url).group()
        # page = 'page' + str(response.meta['page'])
        # typeid = 'typeid' + str(response.meta['typeid'])
        img_url = response.xpath('//div[@id="works_list"]//a[1]/img/@src').extract()[0]
        # if img_url in a:
        #     a[img_url].append(id + page + typeid)
        # else:
        #     a[img_url] = [id + page + typeid]

        if not img_url.startswith('http://www.dgdesign.org.cn'):
            img_url = 'http://www.dgdesign.org.cn' + img_url[2:]
        message = response.xpath('//div[@id="works_list"]//td[2]//div[1]/span/text()').extract()
        remark = ''
        print(img_url)
        item['img_url'] = img_url.strip()
        item['title'] = message[0].strip()
        try:
            item['company'] = message[4].strip()
        except:
            item['company'] = ''
        item['prize_time'] = str(self.year)
        item['remark'] = remark
        item['tags'] = [message[1]]
        item['designer'] = message[3].strip()
        for key, value in data.items():
            item[key] = value
        # for key, value in a.items():
        #     if len(value) > 1:
        #         print(value)
        yield item

# import re
# a = {}

# 2011,2010  552条
# class DesignCaseSpider(scrapy.Spider):
#     name = 'dongguan'
#     allowed_domains = ['www.dgawards.com']
#     year = 2011  # 2011,2010
#     page = 1
#     url = 'http://www.dgdesign.org.cn/'
#     start_urls = [url + str(year)]
#
#     def parse(self, response):
#         a_list = response.xpath('//a/@href').extract()
#         design_list = []
#         for a in a_list:
#             if a.startswith('work_info.asp?'):
#                 design_list.append(a)
#         for design in design_list:
#             yield scrapy.Request(url='http://www.dgdesign.org.cn/' + str(self.year) + '/' + design,
#                                  callback=self.parse_detail, dont_filter=True)
#         page = 14
#         if self.page < int(page):
#             self.page += 1
#             yield scrapy.Request(self.url + str(self.year) + '/?page=' + str(self.page),
#                                  callback=self.parse, dont_filter=True)
#         if self.page == int(page):
#             if self.year > 2010:
#                 self.year -= 1
#                 self.page = 1
#                 yield scrapy.Request(self.url + str(self.year), callback=self.parse,
#                                      dont_filter=True)
#
#     def parse_detail(self, response):
#         item = DesignItem()
#         # id = re.compile('\?id=\w+').search(response.url).group()
#         # page = 'page'+str(response.meta['page'])
#         # year = 'year'+str(response.meta['year'])
#         img_url = response.xpath('//img/@src').extract()[1]
#         # if img_url in a:
#         #     a[img_url].append(id+page+year)
#         # else:
#         #     a[img_url] = [id+page+year]
#         if not img_url.startswith('http://www.dgdesign.org.cn'):
#             if img_url.startswith('..'):
#                 img_url = 'http://www.dgdesign.org.cn' + img_url[2:]
#             elif img_url.startswith('/upload'):
#                 img_url = 'http://www.dgdesign.org.cn' + img_url
#         message = response.xpath('//span/text()').extract()
#         remark = ''
#         item['img_url'] = img_url.strip()
#         item['title'] = message[1]
#         try:
#             item['company'] = message[5]
#         except:
#             item['company'] = ''
#         item['prize_time'] = str(self.year)
#         item['remark'] = remark
#         item['tags'] = [message[2]]
#         try:
#             item['designer'] = message[4]
#         except:
#             item['designer'] = ''
#         for key, value in data.items():
#             item[key] = value
#         yield item
