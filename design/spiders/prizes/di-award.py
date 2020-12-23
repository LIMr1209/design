# -*- coding: utf-8 -*-
import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'di-award',
    'evt': 3,
}


class ChinagoodSpider(scrapy.Spider):
    name = 'di-award'
    year = "2016"
    url = 'https://www.di-award.org/api/2019official/home/online_work_list?page_size=12&page=%s&year=%s&category_id=&award_type=%s&award_group=1&timeStamp=1606203763&random=-TJ3PJ&signature=47D1027899EADE98FAEED37DC4D1C727'
    level_dict = {
        1: "金奖",
        2: "银奖",
        3: "铜奖",
        4: "佳作奖"
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.DesignDownloaderMiddleware': 543,
        }
    }

    def start_requests(self):
        for i in self.level_dict.keys():
            yield scrapy.Request(self.url % (1, self.year, i), callback=self.parse, meta={'level': i, "page": 1})
        # yield scrapy.Request(self.url % (1, self.year, 4), callback=self.parse, meta={'level': 4, "page": 1})
    def parse(self, response):
        page = response.meta['page']
        level = response.meta['level']
        detail_list = json.loads(response.text)['data']['list']
        for i in detail_list:
            item = DesignItem()
            item['title'] = i['title']
            prize = {}
            prize['id'] = 310
            # prize['id'] = 401
            prize['level'] = self.level_dict[level]
            prize['time'] = self.year
            item['prize'] = json.dumps(prize)
            url = 'https://www.di-award.org/collections/detail/%s.html'%(i['id'])
            item['url'] = url
            yield scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True, meta={'item': item})
        if detail_list:
            page += 1
            yield scrapy.Request(self.url % (page, self.year, level), callback=self.parse, meta={'level': level, "page": page})

    def parse_detail(self, response):
        item = response.meta['item']
        img_urls = list(set(response.xpath('//div[contains(@class,"swiper-slide")]/img/@src').extract()))
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://cdn.di-award.org' + img_urls[i]
        item['img_urls'] = ','.join(img_urls)
        remark = response.xpath('//p[@class="fs16"]/text()').extract()
        try:
            customer = response.xpath('//b[contains(text(), "所属单位")]/following-sibling::span[1]//text()').extract()[0]
        except:
            customer = ''
        try:
            company = response.xpath('//b[contains(text(), "设计单位")]/following-sibling::span[1]//text()').extract()[0]
        except:
            company = ''
        try:
            designer = response.xpath('//b[contains(text(), "主创团队")]/following-sibling::span[1]//text()').extract()[0]
        except:
            designer = ''
        item['customer'] = customer
        item['designer'] = designer
        item['company'] = company
        item['description'] = remark
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
