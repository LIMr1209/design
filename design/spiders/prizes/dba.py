# -*- coding: utf-8 -*-
import json
import re

import scrapy
from design.items import DesignItem

# dba 设计奖
data = {
    'channel': 'effec',
    'evt': 3,
}


class EffecSpider(scrapy.Spider):
    name = 'dba'
    allowed_domains = ['www.effectivedesign.org.uk']
    year = 2013
    url = 'http://www.effectivedesign.org.uk/winners/'
    start_urls = [url + str(year)]

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

    def parse(self, response):
        category_list = response.xpath('//ul[@id="sub-nav"]//a/@href').extract()
        for cate_url in category_list:
            # cate = cate_url.split('/')[-1]
            # if cate not in ['bronze','grand-prix','silver','gold']:
            #     continue
            yield scrapy.Request(url='http://www.effectivedesign.org.uk' + cate_url, callback=self.parse_category)
        if self.year < 2020:
            self.year += 1
            yield scrapy.Request(url=self.url + str(self.year), callback=self.parse)

    def parse_category(self, response):
        design_list = response.xpath('//ul[@class="gpWinnersInCategory gp itemList"]//div[@class="in"]')
        level = response.xpath('//ul[@id="sub-nav"]//a[@class="active"]/text()').extract()[0]  # 标签
        prize_level = ''
        if level == 'Bronze':
            prize_level = 'Bronze/铜奖'
        elif level == 'Grand Prix':
            prize_level = 'Grand prix/大奖'
        elif level == 'Silver':
            prize_level = 'Silver/银奖'
        elif level == 'Gold':
            prize_level = 'Gold/金奖'
        for design in design_list:
            item = DesignItem()
            prize = {}
            title = design.xpath('.//h3[@class="projectTitle"]//a/text()').extract()[0]
            page_level = design.xpath('.//p[@class="award"]/text()').extract()
            if page_level:
                if page_level[0].split(', ')[0] == 'Bronze':
                    prize_level = 'Bronze/铜奖'
                elif page_level[0].split(', ')[0] == 'Grand Prix':
                    prize_level = 'Grand prix/大奖'
                elif page_level[0].split(', ')[0] == 'Silver':
                    prize_level = 'Silver/银奖'
                elif page_level[0].split(', ')[0] == 'Gold':
                    prize_level = 'Gold/金奖'
            try:
                designer_name = design.xpath('.//p[@class="agency"]/text()').extract()[1].strip()
            except:
                designer_name = design.xpath('.//p[@class="agency"]/text()').extract()[0].strip()
            detail_url = design.xpath('.//a[1]/@href').extract()[0]
            prize['id'] = 306
            prize['time'] = str(re.findall('(\d+)',response.url)[0])
            prize['level'] = prize_level
            item['title'] = title  # 标题
            item['prize'] = json.dumps(prize)# 奖项级别
            item['designer'] = designer_name  # 设计者

            for key, value in data.items():
                item[key] = value
            yield scrapy.Request(url='http://www.effectivedesign.org.uk' + detail_url, callback=self.parse_detail,
                                 meta={'item': item})

    def parse_detail(self, response):
        item = response.meta['item']

        img_urls = response.xpath('//div[@class="item-list"]//img/@src').extract()
        customer = response.xpath('//div[@class="projectIntro"]/h2[2]/text()').extract()[0]
        description_list = response.xpath('//div[@class="details bodyContent"]/p/text()').extract()
        description = '\n'.join(description_list)
        item['url'] = response.url
        item['img_urls'] = ','.join(img_urls)
        item['customer'] = customer.strip()
        item['description'] = description
        yield item
