import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "montblanc"
    allowed_domains = ["www.montblanc.cn"]
    start_urls = [
        "https://www.montblanc.cn/zh-cn/collection/leather.html?filter=-919261761,1685086427"
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
        detail_url = response.xpath('//div[@class="mb-prod-tile-section"]/a/@href').extract()
        for i in detail_url:
            yield scrapy.Request('https://www.montblanc.cn'+i, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[contains(@class,"mb-pdp-carousel-item slick-slide")]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'https://www.montblanc.cn%s' % img_urls[i]
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'montblanc'
        yield item
