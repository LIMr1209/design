import scrapy
from design.items import DesignItem
from scrapy.selector import HtmlXPathSelector,Selector
import re

data = {
    'channel': '51design',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = '51design'
    allowed_domains = ['www.51design.com']
    page = 1
    start_urls = ['https://www.51design.com/project/index/index/cid/1.html']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="col-3"]/div/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('https://www.51design.com'+i, callback=self.parse_detail)
        page = response.xpath('//ul[@class="pagination my-4"]/li[last()-1]//text()').extract()[0]

        if self.page < int(page):
            self.page += 1
            yield scrapy.Request(url='https://www.51design.com/project/index/index/cid/1.html?cid=1&category=1&is_published=1&page='+str(self.page),callback=self.parse)


    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//ul[@id="gallery-slider"]/li/img/@src').extract()
        tags = ','.join(response.xpath('//div[@class="article-tag pull-left"]/span/text()').extract())
        title = response.xpath('//div[@class="col-md-8"]/h3/text()').extract()[0]
        remark = ''.join(response.xpath('//div[@id="article_content"]/p//text()').extract())
        designer = response.xpath('//h6/span[1]/text()').extract()[0]
        item['designer'] = designer
        item['tags'] = tags
        item['sub_title'] = title.strip()
        item['title'] = title.strip()
        item['remark'] = remark.strip()
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        for key, value in data.items():
            item[key] = value
        yield item
