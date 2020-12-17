# 京东电商
import json
import re

import scrapy
from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "jd_good"
    # allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.price_range = ''
        super(JdSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for i in range(0,20):
            self.browser.get(
                "https://search.jd.com/Search?keyword=%s&page=%d&s=53" % (
                    self.key_words, i))
            urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
            request_urls = []
            for i in urls:
                request_urls.append(i.get_attribute('href'))
            for url in request_urls:
                yield scrapy.Request(url, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = TaobaoItem()
        item['title'] = response.xpath('//div[@class="sku-name"]/text()').extract()[1]
        item['promotion_price'] = response.xpath('//span[@class="p-price"]/span[2]/text()').extract()[0]
        item['original_price'] = response.xpath('//del[@id="page_origin_price"]/text()').extract()[0][1:]
        comment_count = response.xpath('//a[contains(@class,"count J-comm")]/text()').extract()[0][1:]
        index = comment_count.find('万')
        if index != -1:
            item['comment_count'] = int(float(comment_count[:index]) * 10000)
        else:
            comment_count = re.search('\d+', comment_count)
            if comment_count:
                item['comment_count'] = int(comment_count.group())
        item['category'] = self.key_words
        item['service'] = ','.join(response.xpath('//div[@id="J_SelfAssuredPurchase"]/div[@class="dd"]//a/@title').extract())
        reputation_keys = response.xpath('//span[@class="score-desc"]/text()').extract()
        reputation_values = response.xpath('//span[@class="score-detail"]/em/text()').extract()
        reputation_list = []
        for i in range(len(reputation_keys)):
            reputation_list.append(reputation_keys[i]+": "+reputation_values[i])
        item['url'] = response.url
        item['reputation'] =' '.join(reputation_list)
        detail_keys = response.xpath('//dl[@class="clearfix"]/dt/text()').extract()
        detail_values = response.xpath('//dl[@class="clearfix"]/dd/text()').extract()
        detail_dict = {}
        detail_str_list = []
        for i in range(len(detail_keys)):
            detail_str_list.append(detail_keys[i] + ':' + detail_values[i])
            detail_dict[detail_keys[i]] = detail_values[i]
        item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
        item['detail_str'] = ', '.join(detail_str_list)
        img_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'http://img10.360buyimg.com/n12/%s' % img_urls[i]
        item['price_range'] = self.price_range
        itemId = re.findall('\d+',response.url)[0]
        item['out_number'] = itemId
        item['site_from'] = 11
        item['site_type'] = 1
        cover_url = 'http://img10.360buyimg.com/n12/%s'%(response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()[0])
        item['cover_url'] = cover_url
        yield item
