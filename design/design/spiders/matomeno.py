import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'matomeno',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'matomeno'
    allowed_domains = ['matomeno.in']
    page = 1
    start_urls = ['https://matomeno.in']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="c-list4__card"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i, callback=self.parse_detail)
        if self.page < 27:
            self.page += 1
            yield scrapy.Request(url='https://matomeno.in/page/'+str(self.page),callback=self.parse,dont_filter=True)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url

        img_urls = response.xpath('//div[@class="c-entry1"]/img/@src').extract()
        if not img_urls:
            img_urls = response.xpath('//div[@class="box10"]/div[@class="box"][1]/p[2]/a/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('https://matomeno.in'):
                img_urls[i] = 'https://matomeno.in' + img_urls[i]
        remark = ",".join(response.xpath('//div[@class="c-entry1"]/p/text()').extract())
        title = ','.join(response.xpath('//div[@class="c-title1"]/*/text()').extract())
        item['title'] = title
        item['remark'] = remark
        item['url'] = url
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        for key, value in data.items():
            item[key] = value
        yield item
