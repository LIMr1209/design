import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "samsonite"
    allowed_domains = ["www.samsonite.com.cn"]
    start_urls = [
        "https://www.samsonite.com.cn/c/luggage"
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }


    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_list, meta={'usedSelenium': True})

    def parse_list(self, response):
        detail_url = response.xpath('//div[@class="wrapper-box"]/a/@href').extract()
        for i in detail_url:
            yield scrapy.Request('https://www.samsonite.com.cn'+i, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        other_url = response.xpath(
            '//div[@class="goods-color "]/span/@data-url').extract()
        other_url = list(set(other_url))
        for i in other_url:
            yield scrapy.Request('https://www.samsonite.com.cn'+i, callback=self.parse_other, meta={'usedSelenium': True})
        item = ProduceItem()
        img_urls = response.xpath('//div[contains(@class,"img-item")]/@data-src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'https://www.samsonite.com.cn%s' % img_urls[i]
        if not img_urls:
            a = 1
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'samsonite'
        yield item

    def parse_other(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[contains(@class,"img-item")]/@data-src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'https://www.samsonite.com.cn/%s' % img_urls[i]
        if not img_urls:
            a = 1
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'samsonite'
        yield item