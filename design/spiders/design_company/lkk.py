import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'lkk',
    'evt': 3,
    'company': '北京洛可可科技有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'lkk'
    allowed_domains = ['www.lkkdesign.com']
    category = {'73': '新工业设备', '75': '新医疗健康', '76': '新智能硬件', '77': '新生活消费', '80': '新智能出行', '79': '机器人设计','95':'空净产品设计','96':'新能源产品设计','114':'孕婴童产品设计'}
    category_list = ['73', '75', '76', '77', '80', '79','95','96','114']
    category_index = 0
    url = 'http://www.lkkdesign.com/product-index-classifyid-'+category_list[category_index]+'-hyid-.html'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//li[@class="products-hoverlist"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.lkkdesign.com'+i, callback=self.parse_detail)
        if self.category_index < 8:
            self.category_index += 1
            yield scrapy.Request('http://www.lkkdesign.com/product-index-classifyid-'+self.category_list[self.category_index]+'-hyid-.html',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        print(self.category_index)
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        img_urls = response.xpath('//div[@class="product-banner product-banner-video"]/img/@src').extract()
        img_urls.extend(response.xpath('//div[@class="product-banner-txt"]//img/@src').extract())
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.lkkdesign.com' + img_urls[i]
        remark = response.xpath('//div[@class="product-banner-txt"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//h1/text()').extract()[0]
        item['title'] = title
        item['sub_title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
