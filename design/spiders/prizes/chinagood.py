# -*- coding: utf-8 -*-
import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'chinagood',
    'evt': 3,
}


class ChinagoodSpider(scrapy.Spider):
    name = 'chinagood'
    year = 2017  # 2016,2015
    prize_index = 1
    page = 1
    url = 'http://www.chinagooddesignaward.com/online-exhibition/index.php?u=search-index&mid=4&' + 'awards=' + str(
        prize_index) + '&categories=0&nianfen=' + str(year) + '&guolv=0&keyword='
    prize_level = ['', '金奖', '荣誉奖', '优胜奖']

    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//div[@id="am-container"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(url='http://www.chinagooddesignaward.com' + i, callback=self.parse_detail)
        page = response.xpath('//div[@class="pages cf"]/text()').extract()[0]
        page = page[page.find('/') + 2:]
        if self.page < int(page):
            self.page += 1
            page_url = 'http://www.chinagooddesignaward.com/online-exhibition/index.php?search-index-mid-4-awards-' + str(
                self.prize_index) + '-nianfen-' + str(self.year) + '-categories-0-guolv-0-keyword--page-' + str(
                self.page) + '.html'
            yield scrapy.Request(url=page_url, callback=self.parse)
        else:
            if self.prize_index < 3:
                self.page = 1
                self.prize_index += 1
                url = 'http://www.chinagooddesignaward.com/online-exhibition/index.php?u=search-index&mid=4&' + 'awards=' + str(
                    self.prize_index) + '&categories=0&nianfen=' + str(self.year) + '&guolv=0&keyword='
                yield scrapy.Request(url=url, callback=self.parse)
            else:
                if self.year > 2015:
                    self.page = 1
                    self.prize_index = 1
                    self.year -= 1
                    url = 'http://www.chinagooddesignaward.com/online-exhibition/index.php?u=search-index&mid=4&' + 'awards=' + str(
                        self.prize_index) + '&categories=0&nianfen=' + str(self.year) + '&guolv=0&keyword='
                    yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        item = DesignItem()
        prize = {}
        prize['id'] = 15
        prize['time'] = self.year
        prize['level'] = self.prize_level[self.prize_index]
        prize['name'] = '中国好设计奖'
        url = response.url
        img_urls = response.xpath('//div[@class="main_image"]/ul/li/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http://www.chinagooddesignaward.com'):
                img_urls[i] = 'http://www.chinagooddesignaward.com' + img_urls[i]
        remark = response.xpath('//div[@class="ct_cn"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        title = response.xpath('//h2/text()').extract()[0]
        designer = response.xpath('//div[@class="case_text"]/dl[2]/dd/p//text()').extract()
        designer = [''.join(i.split()) for i in designer]
        designer = ' '.join(designer)
        company = response.xpath('//div[@class="case_text"]/dl[1]/dd/p[1]//text()').extract()
        company = ' '.join(company)
        if len(remark) > 480:
            remark = remark[:480]
        item['title'] = title
        item['sub_title'] = title
        item['remark'] = remark
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        item['designer'] = designer
        item['company'] = company
        item['prize'] = json.dumps(prize)
        for key, value in data.items():
            item[key] = value
        yield item
