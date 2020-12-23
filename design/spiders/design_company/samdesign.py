import scrapy
from design.items import DesignItem
import json
import re
data = {
    'channel': 'samdesign',
    'evt': 3,
    'company': '深圳市迪特格工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'samdesign'
    allowed_domains = ['www.sam-id.com']
    category = {'215': '新能源', '213': '交通工具', '207': '经典案例', '211': '消费电子','212':'日常用品','208':'机械设备','209':'智能终端','210':'智能家电','214':'机器人'}
    category_list = ['215','213','207','211','212','208','209','210','214']
    category_index = 0
    url = 'http://www.sam-id.com/index.php/Index/product/c1/3/c2/'+category_list[category_index]
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//li[@class="products-hoverlist"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.sam-id.com'+i, callback=self.parse_detail,dont_filter=True)
        if self.category_index < 8:
            self.category_index += 1
            yield scrapy.Request('http://www.sam-id.com/index.php/Index/product/c1/3/c2/'+self.category_list[self.category_index],callback=self.parse,dont_filter=True)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        img_urls = response.xpath('//div[@class="product-banner-txt"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.sam-id.com' + img_urls[i]
        remark = response.xpath('//div[@class="product-banner-txt"]/p//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ' '.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        try:
            title = response.xpath('//div[@class="product-banner-txt"]/*[1]//text()').extract()[0]
        except:
            title = '概念车设计'
        item['title'] = title
        item['sub_title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
