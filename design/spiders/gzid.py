import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'gzid',
    'evt': 3,
    'company': '广州市原子工业产品科技发展有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'gzid'
    allowed_domains = ['www.gzid.cn']
    category = {'1090752': '数码电子', '1126484': '医疗护理', '1126485': '家居生活', '1233806': '办公用品', '1126486': '专业产品', '1233803': '儿童用品','1233804':'工程结构'}
    category_list = ['1090752', '1126484', '1126485', '1233806', '1126486', '1233803','1233804']
    category_index = 0
    url = 'http://www.gzid.cn/CategoryResultlist?EntityTypeName=product&categoryId='+category_list[category_index]
    start_urls = [url]


    def parse(self, response):
        detail_list = response.xpath('//li[@class="w-list-item"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.gzid.cn'+i, callback=self.parse_detail)

        if self.category_index < 6:
            self.category_index += 1
            yield scrapy.Request(url = 'http://www.gzid.cn/CategoryResultlist?EntityTypeName=product&categoryId='+self.category_list[self.category_index],callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        img_urls = response.xpath('//div[@class="limitimg"]/p/img/@src').extract()

        title = response.xpath('//h1/text()').extract()[0]
        item['title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
