# -*- coding: utf-8 -*-
import json

import scrapy
from design.items import DesignItem

# 意大利 Compasso d`Oro设计奖


class DesignCaseSpider(scrapy.Spider):
    name = 'adi-design'
    # allowed_domains = ['www.adi-design.org']
    start_urls = ['https://www.adi-design.org/tutte-le-edizioni-del-compasso-d-oro.html']

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES' : {
            'design.pipelines.ImagePipeline': 301,
        }
    }
    def parse(self, response):
        year_list = response.xpath('//div[@class="cell large-9"]/strong/a/@href').extract()
        for year_url in year_list:
            yield scrapy.Request(year_url, callback=self.parse_detail)

    def parse_detail(self, response):
        img_url_list = response.xpath('//div[@class="item-inner"]//img/@src').extract()
        title_list = response.xpath('//div[@class="item-inner"]/a/@title').extract()
        year = response.xpath('//h2/text()').extract()[0][:4]
        if not year.isdigit:
            year = '2016'
        for i in range(len(img_url_list)):
            item = DesignItem()
            prize = {}
            prize['id'] = 305
            prize['time'] = year
            img_urls = img_url_list[i]
            item['prize'] = json.dumps(prize, ensure_ascii=False)
            item['url'] = response.url
            item['img_urls'] = img_urls
            item['evt'] = 3
            item['channel'] = "adi-design"
            title_list[i] = title_list[i][:200]
            item['title'] = title_list[i]
            yield item
