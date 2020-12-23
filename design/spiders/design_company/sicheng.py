import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'sicheng',
    'evt': 3,
    'company': '北京思乘创新工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'sicheng'
    allowed_domains = ['www.thinkpower.cc']
    start_urls = ['http://www.thinkpower.cc/Item/list.asp?id=1779']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="xn_c_index_42_nrsmall"]/div/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i, callback=self.parse_detail)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = response.xpath('//span[@class="n_r_wz6"]/a/text()').extract()[0]
        img_urls = response.xpath('//a[@onclick]/img/@src').extract()
        title = response.xpath('//*[@id="xn_c_prodv_60_nameText"]/text()').extract()[0]
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
