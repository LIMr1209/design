import scrapy
from design.items import DesignItem
import re

data = {
    'channel': 'siwei',
    'evt': 3,
    'company':'深圳市思为工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'siwei'
    allowed_domains = ['www.siwei_id.com']
    start_urls = ['http://www.siwei-id.com/page-75528.html']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="image-w"]/a')
        detail_list.pop()
        for i in detail_list:
            url = i.xpath('./@href').extract()[0]
            title = i.xpath('./@title').extract()[0]
            yield scrapy.Request('http://www.siwei-id.com'+url, callback=self.parse_detail,meta={'title':title},dont_filter=True)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//ul[@class="bxslider"]/li/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.siwei-id.com' + img_urls[i]
        title = response.meta['title']
        remark = response.xpath('//div[@class="w-text"]/p/text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ','.join(remark)
        item['title'] = title.strip()
        item['url'] = url
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)

        for key, value in data.items():
            item[key] = value
        yield item
