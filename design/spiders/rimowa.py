import re

import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "rimowa"
    allowed_domains = ["www.rimowa.com"]
    start_urls = [
        "https://www.rimowa.com/cn/zh/全部行李箱/?start=%s&sz=12&format=page-element&loopIndex=%s"
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
        for i in [0,12,24,36,48,60]:
            self.browser.get(self.start_urls[0]%(i,i+1))
            urls = self.browser.find_elements_by_xpath('//a[@class="product-link"]')
            request_urls = []
            for i in urls:
                request_urls.append(i.get_attribute('href'))
            for url in request_urls:
                yield scrapy.Request(url, callback=self.parse, meta={'usedSelenium': True})
        # yield scrapy.Request('https://www.rimowa.com/cn/zh/luggage/colour/titanium/cabin-s/92552034.html#start=1',
        #                      callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        other_url = response.xpath(
            '//li[@class="selectable c-variations__item u-hide-on-matte u-hide-on-acetate u-hide-on-rim"]/a/@href').extract()
        other_url = list(set(other_url))
        for i in other_url:
            yield scrapy.Request(i, callback=self.parse_other, meta={'usedSelenium': True})
        item = ProduceItem()
        b = re.findall('"image": \["(.*)"\]', response.text)
        img_urls = b[0].split('","')
        # for i in range(len(img_urls)):
        #     img_urls[i] = 'https://www.rimowa.com%s' % img_urls[i]
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'rimowa'
        yield item

    def parse_other(self, response):
        item = ProduceItem()
        b = re.findall('"image": \["(.*)"\]', response.text)
        img_urls = b[0].split('","')
        # for i in range(len(img_urls)):
        #     img_urls[i] = 'https://www.rimowa.com%s' % img_urls[i]
        item['tag'] = "拉杆箱"
        item['img_urls'] = img_urls
        item['channel'] = 'rimowa'
        yield item
