# -*- coding: utf-8 -*-
import json

import scrapy
from design.items import DesignItem

# DBA设计效能奖
data = {
    'channel': 'effec',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'design_case'
    allowed_domains = ['www.effectivedesign.org.uk']
    year = 2018
    url = 'http://www.effectivedesign.org.uk/winners/'
    start_urls = [url + str(year)]

    def parse(self, response):
        category_list = response.xpath('//ul[@id="sub-nav"]//a/@href').extract()
        for cate_url in category_list:
            yield scrapy.Request(url='http://www.effectivedesign.org.uk' + cate_url, callback=self.parse_category)
        if self.year > 2013:
            self.year -= 1
            yield scrapy.Request(url=self.url + str(self.year), callback=self.parse)

    def parse_category(self, response):
        design_list = response.xpath('//ul[@class="gpWinnersInCategory gp itemList"]//div[@class="in"]')
        tags = response.xpath('//ul[@id="sub-nav"]//a[@class="active"]/text()').extract()[0]  # 标签
        for design in design_list:
            item = DesignItem()
            prize = {}
            title = design.xpath('.//h3[@class="projectTitle"]//a/text()').extract()[0]
            prize_level = design.xpath('.//p[@class="award"]/text()').extract()[0]
            try:
                designer_name = design.xpath('.//p[@class="agency"]/text()').extract()[1].strip()
            except:
                designer_name = design.xpath('.//p[@class="agency"]/text()').extract()[0].strip()
            detail_url = design.xpath('.//a[1]/@href').extract()[0]
            prize['id'] = 20
            prize['name'] = 'DBA设计效能奖'
            prize['time'] = str(self.year + 1)
            prize['level'] = prize_level
            item['title'] = title  # 标题
            item['sub_title'] = title
            item['tags'] = tags
            item['prize'] = json.dumps(prize)# 奖项级别
            item['designer'] = designer_name  # 设计者

            for key, value in data.items():
                item[key] = value
            yield scrapy.Request(url='http://www.effectivedesign.org.uk' + detail_url, callback=self.parse_detail,
                                 meta={'item': item})

    def parse_detail(self, response):
        item = response.meta['item']

        img_urls = response.xpath('//div[@class="item-list"]//img/@src').extract()
        company = response.xpath('//div[@class="projectIntro"]/h2[3]/a/text()').extract()[0]
        remark = response.xpath('//div[@class="details bodyContent"]/p/text()').extract()[0]
        if len(remark) > 450:
            remark = remark[:450]
        item['url'] = response.url
        item['img_urls'] = ','.join(img_urls)
        item['company'] = company.strip()
        item['remark'] = remark.replace('\n','').replace(' ','').replace('\r','').strip()
        yield item
