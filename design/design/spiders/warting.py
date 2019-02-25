import scrapy
from design.items import DesignItem
import re

data = {
    'channel': 'warting',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'warting'
    allowed_domains = ['www.warting.com']
    page = 1
    start_urls = ['http://www.warting.com/gallery/industry/']

    def parse(self, response):
        detail_list = response.xpath('//ul[@class="clearfix"]/li/a/@href').extract()
        print(detail_list)
        for i in detail_list:

            yield scrapy.Request('http://www.warting.com'+i, callback=self.parse_detail)

        if self.page < 55:
            self.page += 1
            yield scrapy.Request(url='http://www.warting.com/gallery/industry/list_'+str(self.page)+'.html',
                                 callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        title = response.xpath('//h1/text()').extract()[0]
        img_urls = response.xpath('//ul[@id="picInGG"]/li/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i][:img_urls[i].find('jpg?')+3]
        tags = response.xpath('//div[@class="fleft article_tags"]/a/text()').extract()
        tags = ','.join(tags)
        item['tags'] = tags
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['title'] = title
        item['sub_title'] = title
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item

