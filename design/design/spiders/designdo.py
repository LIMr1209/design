import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'designdo',
    'evt': 3,
    'company': '深圳市鼎典工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'designdo'
    allowed_domains = ['www.designdo.cn']
    category_id = 1
    url = 'http://www.designdo.cn/index.php/Case/index/id/'+str(category_id)+'.html'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//div[@class="grid"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.designdo.cn'+i, callback=self.parse_detail)
        if self.category_id < 6:
            self.category_id += 1
            yield scrapy.Request('http://www.designdo.cn/index.php/Case/index/id/'+str(self.category_id)+'.html',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = response.xpath('//li[contains(@class," li_active1")]/a/text()').extract()[0]
        img_urls = response.xpath('//div[@class="view_content"]/p/img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.designdo.cn' + img_urls[i]
        try:
            remark = response.xpath('/html/body/div[9]/div[1]/table/tr/td[1]/p[2]/span/text()').extract()[0]
        except:
            remark = ''
        title = response.xpath('//p[@class="case_title"]/text()').extract()[0]
        item['title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
