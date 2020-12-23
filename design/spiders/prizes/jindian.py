# -*- coding: utf-8 -*-
import scrapy
import json
from design.items import DesignItem

# 中国家具设计金点奖
data = {
    'channel': 'jiagle',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'jindian'
    allowed_domains = ['gida.jiagle.com']
    id = 2  # 2,3,4,5,6,7
    start_urls = ['http://gida.jiagle.com/match/' + str(id) + '.html']

    def parse(self, response):
        design_list = response.xpath('//li[contains(@class,"ft")]/a/@href').extract()
        tags = response.xpath('//li[@class="active"]/a/text()').extract()[0]
        for design in design_list:
            yield scrapy.Request(design, callback=self.parse_detail,
                                 meta={'tags': tags})
        if self.id < 7:
            self.id += 1
            yield scrapy.Request('http://gida.jiagle.com/match/' + str(self.id) + '.html', callback=self.parse)

    def parse_detail(self, response):
        prize = {'id':22,'name':'中国家具设计金点奖','level':'','time':''}

        url = response.url
        item = DesignItem()
        tags = response.meta['tags']
        img_urls = response.xpath('//div[@class="st-detail-small clearfix"]/ul/li[position()>1]//img/@src').extract()
        if not img_urls:
            img_urls = response.xpath('//div[@class="st-detail-small clearfix"]/ul/li//img/@src').extract()
        message = response.xpath('//div[@class="detail-title"]//dd/text()').extract()
        title = message[0]
        company = message[1]
        designer = message[2]
        remark = response.xpath('//div[@class="detail-text-box"]/p/text()').extract()[0]
        remark = remark.replace('\n','').replace(' ','').replace('\r','').strip()
        item['url'] = url
        item['prize'] = json.dumps(prize)
        item['img_urls'] = ','.join(img_urls)
        item['title'] = title.strip()
        item['sub_title'] = title.strip()
        item['company'] = company.strip()
        item['remark'] = remark
        item['tags'] = tags
        item['designer'] = designer.strip()
        for key, value in data.items():
            item[key] = value
        yield item
