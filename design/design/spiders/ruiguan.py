import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'ruiguan',
    'evt': 3,
    'company': '瑞观智选工业设计（北京）有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'ruiguan'
    allowed_domains = ['www.kcandesign.com']
    start_urls = ['http://www.kcandesign.com/']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="prop"]/p/a')
        detail_list.pop(0)
        for i in detail_list:
            url = i.xpath('./@href').extract()[0]
            title = i.xpath('./text()').extract()[0]
            yield scrapy.Request('http://www.kcandesign.com/'+url, callback=self.parse_detail,meta={'title':title})

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_url = response.xpath('//div[@class="col-md-12 col-sm-12 col-xs-12"]/img/@src').extract()[0]
        if not img_url.startswith('http'):
            img_url = 'http://www.kcandesign.com/'+img_url
        remark = response.xpath('//div[contains(@class,"page_text")]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ' '.join(remark)
        title = response.meta['title']
        item['title'] = title
        item['img_url'] = img_url
        item['url'] = url
        item['remark'] = remark
        # print(remark)
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
