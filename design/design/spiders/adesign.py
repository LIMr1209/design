# -*- coding: utf-8 -*-
import re

import scrapy
from design.items import DesignItem


data = {
    'channel': 'adesign',
    'evt': 3,
    'prize_id': 23,
    'prize': 'A 设计大奖',
}


class ChinagoodSpider(scrapy.Spider):
    name = 'adesign'
    # 2010-2014
    # url = 'http://www.awardwinningdesign.org/'
    # 2015-2018
    url = 'http://www.awardeddesigns.com/'
    start_urls = [url]

    def parse(self, response):
        # detail_list = response.xpath('//body/div[1]/a/@href').extract()
        detail_list = response.xpath('//body/div/div[position()>2]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i,callback=self.parse_detail)

    def parse_detail(self,response):
        item = DesignItem()
        text = response.xpath('/html/body/table[1]/tr[4]/td/span[4]/table/tr[2]/td[2]/h2/text()').extract()[0]
        rex = re.compile(r'Winner in (.*?)Design Category,')
        tags = rex.findall(text)[0]
        if tags.count('and'):
            tags = re.sub(r' and ',',',tags)
        rex = re.compile(r'Category, (.*?) -')
        prize_time = rex.findall(text)[0]
        url = response.url
        remark = ''
        img_url = response.xpath('/html/body/table[1]/tr[3]/td/a/img/@src').extract()[0]
        if not img_url.startswith('http'):
            img_url = 'https://competition.adesignaward.com/' + img_url

        try:
            remark = response.xpath('/html/body/table[1]/tr[3]/td/table/tr[3]/td[1]/text()').extract()
            index = remark.index(" \r\nUNIQUE PROPERTIES / PROJECT DESCRIPTION:")
            remark = remark[index + 1]
            remark = remark.split('\r\n')
            remark = ' '.join(remark)
        except:
            print("*"*100,remark,response.url)

        title = response.xpath('/html/body/table[1]/tr[2]/td/table/tr/td[1]/h1/text()').extract()[0][:-4]
        designer = response.xpath('/html/body/table[1]/tr[2]/td/table/tr/td[1]/h1/a/text()').extract()[0].strip()
        if len(remark) > 480:
            remark = remark[:480]
        item['title'] = title
        item['remark'] = remark
        item['url'] = url
        item['img_url'] = img_url
        item['designer'] = designer
        item['tags'] = tags
        item['prize_time'] = prize_time
        for key, value in data.items():
            item[key] = value
        yield item
        # print(item)


