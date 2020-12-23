import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'blogdeco',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'blogdeco'
    allowed_domains = ['www.blogdecodesign.fr']
    start_urls = ['https://www.blogdecodesign.fr/liste-des-designers/']

    def parse(self, response):
        designer_list = response.xpath('//div[@class="three columns"]//li/a/@href').extract()
        for i in designer_list:
            yield scrapy.Request(i, callback=self.parse_list)

    def parse_list(self,response):
        detail_list = response.xpath('//h2/a/@href').extract()
        for i in detail_list:
            item = DesignItem()
            designer = response.xpath('//h1/text()').extract()[0]
            item['designer'] = designer
            yield scrapy.Request(i,callback=self.parse_detail,meta={'item':item})

    def parse_detail(self, response):
        item = response.meta['item']
        url = response.url
        img_url = response.xpath('//div[@class="center"]//img/@src').extract()[0]
        if not img_url.startswith('https://www.blogdecodesign.fr'):
            img_url = 'https://www.blogdecodesign.fr'+img_url
        title = response.xpath('//h1/text()').extract()[0]
        remark = response.xpath('//div[@class="dp100 postlink"]/p/text()').extract()[0]
        item['title'] = title.strip()
        item['remark'] = remark.strip().replace('\n', '').replace('\n\r', '')
        item['url'] = url
        item['img_url'] = img_url
        for key, value in data.items():
            item[key] = value
        yield item

