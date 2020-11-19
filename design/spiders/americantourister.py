import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "americantourister"
    allowed_domains = ["www.americantourister.com.tw"]
    start_urls = [
        "https://www.americantourister.com.tw/on/demandware.store/Sites-AmericanTouristerTW-Site/zh_TW/Search-UpdateGrid?cgid=luggage&isLoadedMore=true&start=%s&sz=20&selectedUrl=https://www.americantourister.com.tw/on/demandware.store/Sites-AmericanTouristerTW-Site/zh_TW/Search-UpdateGrid?cgid=luggage&isLoadedMore=true&start=%s&sz=20"
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
        for i in [0,20,40]:
            self.browser.get(self.start_urls[0]%(i,i))
            urls = self.browser.find_elements_by_xpath('//div[@class="image-container"]/a')
            request_urls = []
            for i in urls:
                request_urls.append(i.get_attribute('href'))
            for url in request_urls:
                yield scrapy.Request(url, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[contains(@class,"owl-carousel-item")]/img/@src').extract()
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'americantourister'
        yield item

