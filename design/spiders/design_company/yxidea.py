import scrapy
from design.items import DesignItem
import re
import json

data = {
    'channel': 'yxidea',
    'evt': 3,
    'company': '深圳市易形工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'yxidea'
    allowed_domains = ['www.yxidea.com.cn']
    page = 1
    category = {'49': '消费电子', '48': '医疗器械', '11': '智能硬件', '12': '设备类', '64': '音频类', '66': '居家美学'}
    category_list = ['49', '48', '11', '12', '64', '66']
    category_index = 0

    start_urls = ['http://www.yxidea.com.cn/index.php?ac=article&at=list&tid=' + category_list[category_index]]

    def parse(self, response):
        detail_list = response.xpath('//div[@class="grid"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.yxidea.com.cn' + i, callback=self.parse_detail)
        page = response.xpath('//div[@id="Pagination"]/*[last()-2]/text()').extract()[0]
        if self.page < int(page):
            self.page += 1
            yield scrapy.Request(url='http://www.yxidea.com.cn/index.php?ac=article&at=list&tid=' + self.category_list[
                self.category_index] + '&page=' + str(self.page), callback=self.parse)
        else:
            if self.category_index < 5:
                self.page = 1
                self.category_index += 1
                yield scrapy.Request(
                    url='http://www.yxidea.com.cn/index.php?ac=article&at=list&tid=' + self.category_list[
                        self.category_index])

    def parse_detail(self, response):
        img_urls = response.xpath('//div[@id="focus"]/ul/li/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http://www.yxidea.com.cn/'):
                img_urls[i] = 'http://www.yxidea.com.cn/' + img_urls[i]
        item = DesignItem()
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        title = response.xpath('//div[@class="pt10"]/text()').extract()[0]
        item['tags'] = tags
        item['title'] = title.strip()
        item['sub_title'] = title.strip()
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        print(item)
        for key, value in data.items():
            item[key] = value
        yield item
