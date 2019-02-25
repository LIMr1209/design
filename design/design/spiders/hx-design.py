import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'hx-design',
    'evt': 3,
    'company': '上海幻想工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'hx-design'
    allowed_domains = ['www.hx-design.com']
    start_urls = ['http://www.hx-design.com/ylqx.html']
    def parse(self, response):
        category_list = response.xpath('//div[@class="fenl01"]/ul/li/a/@href').extract()
        category_list.pop()
        for i in category_list:
            yield scrapy.Request(i, callback=self.parse_category,dont_filter=True)

    def parse_category(self,response):
        detail_list = response.xpath('//div[@class="pro_main"]/dl/dt/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i,callback=self.parse_detail)
        next_page = response.xpath('//*[@id="pagerMain"]/a[@title="下一页"]')
        if next_page:
            url = next_page.xpath('./@href').extract()[0]
            yield scrapy.Request(url,callback=self.parse_category)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        text = response.xpath('//div[@class="plc"]/a/text()').extract()
        tags = text[2]
        title = text[3]
        img_urls = response.xpath('//div[@class="pro_content"]//img/@src').extract()
        # print(img_urls)
        # print(response.url)
        # print('*'*50)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.hx-design.com' + img_urls[i]

        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)

        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
        # print(item)
