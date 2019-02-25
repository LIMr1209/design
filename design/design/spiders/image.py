# -*- coding: utf-8 -*-
import json

import scrapy
from design.items import DesignItem

# 澳大利亚国际设计大奖
data = {
    'channel': 'gd-design',
    'evt': 3,
}

prize_levels = ['good-design-award-of-the-year', 'good-design-sustainability', 'good-design-award-best-in-class',
                'good-design-award-gold', 'good-design-award-winner']

category_list = {
    'architectural-design': ['commercial-residential', 'interior-design', 'urban-design'],
    'communication-design': ['advertising', 'branding-identity', 'packaging', 'print'],
    'digital-design': ['apps-and-software', 'game-design-animation', 'interface', 'web-design-development'],
    'product-design': ['automotive-transport', 'commercial-industrial', 'consumer-electronics', 'domestic-appliances',
                       'furniture-lighting', 'hardware-building', 'housewares-objects', 'medical-scientific',
                       'sport-lifestyle'],
    'service-design': ['commercial-services', 'education-services', 'public-sector-services'],
    'design-strategy': [],
    'engineering-design': [],
    'fashion-design': [],
    'next-gen': [],
    'social-impact': []

}


class ImageSpider(scrapy.Spider):
    name = 'image'
    allowed_domains = ['https://good-design.org']
    year = 2018
    url = 'https://good-design.org/good-design-index/?yr='
    start_urls = [url + str(year)]

    def parse(self, response):
        for key, value in category_list.items():
            for v in value:
                for prize_level in prize_levels:
                    yield scrapy.Request(
                        url=self.url + str(self.year) + '&discipline=' + v + '&awardtype=' + prize_level,
                        callback=self.parse_list, meta={'prize_level': prize_level}, dont_filter=True)
            else:
                for prize_level in prize_levels:
                    yield scrapy.Request(
                        url=self.url + str(self.year) + '&discipline=' + key + '&awardtype=' + prize_level,
                        callback=self.parse_list, meta={'prize_level': prize_level}, dont_filter=True)
        if self.year > 2014:
            self.year -= 1
            yield scrapy.Request(url=self.url + str(self.year), callback=self.parse, dont_filter=True)

    def parse_list(self, response):
        prize_level = response.meta['prize_level']
        detail_list = response.xpath('//div[contains(@class,"is-one-fifth-widescreen")]/a/@href').extract()
        for detail in detail_list:
            yield scrapy.Request(url=detail, callback=self.parse_detail, meta={'prize_level': prize_level},
                                 dont_filter=True)
        else:
            print('此类别下无奖项')

    def parse_detail(self, response):
        item = DesignItem()
        prize_level = response.meta['prize_level']
        prize_time = response.xpath('//li[@class="project-year project-term"]/h4/text()').extract()[0]
        prize = {}
        prize['id'] = 16
        prize['name'] = '澳大利亚国际设计奖'
        prize['level'] = prize_level
        prize['time'] = prize_time
        tags = response.xpath('//li[@class="project-discipline project-term"]//div/text()').extract()
        for i in range(tags.count(' ')):
            tags.remove(' ')
        designer = response.xpath('//div[@class="columns project-details"]/div[2]//li/text()').extract()[0]
        try:
            company = response.xpath('//div[@class="columns project-details"]/div[3]/div/p/text()').extract()[0]
        except:
            company = ''
        title = response.xpath('//h1/text()').extract()[0]
        img_urls = response.xpath('//div[@class="project-main-content__inner-wrapper"]/figure/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('https://good-design.org'):
                img_urls[i] = 'https://good-design.org' + img_urls[i]
        remark = response.xpath('//div[@class="project-description"]/p[1]/text()').extract()[0]
        remark = remark.replace('\n','').replace(' ','').replace('\r','').strip()
        if len(remark) > 450:
            remark = remark[:450]
        item['prize'] = json.dumps(prize)
        item['url'] = response.url
        item['tags'] = ','.join(tags)
        item['designer'] = designer
        item['company'] = company
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['remark'] = remark
        for key, value in data.items():
            item[key] = value
        print(item)
        yield item
