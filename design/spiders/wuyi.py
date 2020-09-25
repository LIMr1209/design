import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'wuyi',
    'evt': 3,
    'company': '深圳市白狐工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'wuyi'
    allowed_domains = ['www.woodesigncn.com']
    start_urls = ['http://www.woodesigncn.com/product.html']

    def parse(self, response):
        detail_list = response.xpath('//a[@data-toggle]/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.woodesigncn.com'+i, callback=self.parse_detail)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//ul[@id="banner-list"]/li/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.woodesigncn.com' + img_urls[i]
        remark = response.xpath('//div[@class="content"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//h4/text()').extract()[0]
        item['title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        for key, value in data.items():
            item[key] = value
        print(item)
        yield item
