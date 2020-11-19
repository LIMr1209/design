import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "shilladfs"
    allowed_domains = ["www.shilladfs.com"]
    start_urls = [
        "https://www.shilladfs.com/estore/kr/zh/b/cutiesandpals"
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
            '//ul[@class="product_list"]//div[@class="product_over_wrap"]/a[1]/@href').extract()
        for i in detail_url:
            yield scrapy.Request('https://www.shilladfs.com'+i, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//ul[@class="clear_both pd-thumb-list"]//img/@data-image').extract()
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'shilladfs'
        yield item
