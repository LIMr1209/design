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

    def start_requests(self):
        for i in self.level_dict.keys():
            yield scrapy.Request(self.url % (1, self.year, i), callback=self.parse, meta={'level': i, "page": 1})

    def parse(self, response):
        page = response.meta['page']
        level = response.meta['level']
        detail_list = json.loads(response.text)['data']['list']
        for i in detail_list:
            item = DesignItem()
            item['title'] = i['title']
            prize = {}
            prize['id'] = 310
            prize['level'] = self.level_dict[level]
            prize['time'] = self.year
            item['prize'] = json.dumps(prize)
            url = 'https://www.di-award.org/collections/detail/%s.html'%(i['id'])
            item['url'] = url
            yield scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True, meta={'item': item})
        if detail_list:
            page += 1
            yield scrapy.Request(self.url % (page, self.year, level), callback=self.parse, meta={'level': i, "page": 1})

    def parse_detail(self, response):
        item = response.meta['item']
        img_urls = list(set(response.xpath('//div[contains(@class,"swiper-slide")]/img/@src').extract()))
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://cdn.di-award.org' + img_urls[i]

        remark = response.xpath('//p[@class="fs16"]/text()').extract()
        company = response.xpath('//p[@class="fs18 clear"]/b[contains(text(), "所属单位")]').extract()[1]
        item['company'] = company
        item['description'] = remark
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
