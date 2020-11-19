import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "tumi"
    allowed_domains = ["www.tumi.cn"]
    start_urls = [
        "https://www.tumi.cn/c-luggage/carryon-luggage/?q=:relevance&pageSize=60&page=0&sort=relevance"
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
        detail_url = response.xpath(
            '//div[contains(@class,"ctnr-prod-item js-gird-gtm prod_grid")]/div[2]/a/@href').extract()
        for i in detail_url:
            yield scrapy.Request(i, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[contains(@class,"cntr-prod-alternate-item")]/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace("wid=45&hei=45", "wid=620&hei=750").replace("small-1", "1-pc")
            if not img_urls[i].startswith("http"):
                img_urls[i] = "https://www.tumi.cn"+img_urls[i]
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'tumi'
        yield item
