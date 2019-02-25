import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'seeya',
    'evt': 3,
    'company': '上海希雅设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'seeya'
    allowed_domains = ['www.seeyadesign.com']
    url = 'http://www.seeyadesign.com/index.php?s=/home/service/index/p/1.html'
    start_urls = [url]
    page = 1

    def parse(self, response):
        detail_list = response.xpath('//div[@class="service_box"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.seeyadesign.com'+i, callback=self.parse_detail)
        if self.page < 5:
            self.page += 1
            yield scrapy.Request(url='http://www.seeyadesign.com/index.php?s=/home/service/index/p/'+str(self.page)+'.html',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_url = response.xpath('//div[@class="product-banner product-banner-video"]/img/@src').extract()[0]
        if not img_url.startswith('http'):
            img_url = 'http://www.lkkdesign.com'+img_url
        remark = response.xpath('//div[@class="product-banner-txt"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//h1/text()').extract()[0]
        item['title'] = title
        item['remark'] = remark
        item['img_url'] = img_url
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
