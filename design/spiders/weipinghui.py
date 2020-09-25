import re
import time
import scrapy
from design.items import ProduceItem

from design.spiders.selenium import SeleniumSpider


class WeipinSpider(SeleniumSpider):
    name = "weipinghui"
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

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.page = 1
        super(WeipinSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        self.browser.get( "https://category.vip.com/suggest.php?keyword=%s&ff=235|12|1|1" %self.key_words)
        page = self.browser.find_elements_by_xpath('//*[@id="J_pagingCt"]/span[1]')
        page = page[0].text
        page_int = int(re.findall(r"\d+\.?\d*", page)[0])
        if self.page <= page_int:
            yield scrapy.Request(
                "https://category.vip.com/suggest.php?keyword=%s&ff=235|12|1|1&page=%s" % (self.key_words, self.page),
                callback=self.parse_list, meta={'usedSelenium': True})
            self.page += 1

    def parse_list(self,response):
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        urls = self.browser.find_elements_by_xpath('//div[@class="c-goods-item  J-goods-item c-goods-item--auto-width"]/a')
        request_urls = []
        for i in urls:
            request_urls.append(i.get_attribute('href'))
        for url in request_urls:
            yield scrapy.Request(url, callback=self.parse_detail, meta={'usedSelenium': True})


    def parse_detail(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[@id="J-img-content"]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = "https:"+ img_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        item['channel'] = 'weiping'
        yield item
