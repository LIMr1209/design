import scrapy
from design.items import DesignItem
import re

data = {
    'channel': '333cn',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = '333cn'
    allowed_domains = ['www.333cn.com']
    page = 1
    url = 'http://www.333cn.com/zuopin/list-8-'
    start_urls = [url+str(page)+'.html']

    def parse(self, response):
        detail_list = response.xpath('//ul[@class="work_zpul"]/li/a[1]/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.333cn.com'+i, callback=self.parse_detail)

        if self.page < 48:
            self.page += 1
            yield scrapy.Request(url=self.url+str(self.page)+'.html',callback=self.parse)


    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_url = response.xpath('//img[@class="wdcontimg"]/@src').extract()[0]
        tags = ''
        try:
            tags = response.xpath('//div[@class="wdtitconl"]/a[2]/text()').extract()
        except:
            tags = ''
        title = response.xpath('//p[@class="wdtitlp"]/text()').extract()[0]
        item['tags'] = tags
        item['title'] = title.strip()
        item['url'] = url
        item['img_url'] = img_url
        print(item)
        for key, value in data.items():
            item[key] = value
        yield item
