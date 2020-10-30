import json
import requests
import scrapy
from design.spiders.selenium import SeleniumSpider


class BrandSpider(SeleniumSpider):
    name = "brand_baidu"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, key_words=None, *args, **kwargs):
        super(BrandSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        res = requests.get('http://dev.taihuoniao.com/api/brand/list')
        data = json.loads(res.content)['data']
        for i in data:
            yield scrapy.Request("https://baike.baidu.com/item/%s" % i['name'], callback=self.parse_detail,
                                 meta={'usedSelenium': True})


    def parse_detail(self, response):
        item = dict()
        item['name'] = response.xpath('//dt[contains(text(), "中文名")]/following-sibling::dd/text()').extract()[0]
        item['en_name'] = response.xpath('//dt[contains(text(), "外文名")]/following-sibling::dd/text()').extract()[0]
        try:
            item['found_time'] = response.xpath('//dt[contains(text(), "起始时间")]/following-sibling::dd[1]/text()').extract()[0]
        except:
            item['found_time'] = \
            response.xpath('//dt[contains(text(), "成立时间")]/following-sibling::dd[1]/text()').extract()[0]
        item['img_url'] = response.xpath('//div[@class="summary-pic"]//img/@src').extract()[0]
        item['url'] = response.xpath('//dt[contains(text(), "官")]/following-sibling::dd[1]/text()')
        item['country'] = "country"
        item['description'] = 'description'
        res = requests.post('http://dev.taihuoniao.com/api/brand/submit',data=item )
        print(res.content.decode("utf-8"))


