import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'daetu',
    'evt': 3,
    'company': '德腾工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'daetu'
    allowed_domains = ['www.daetumdesign.com']
    start_urls = ['http://www.daetumdesign.com/?anli/Product3/']
    page = 1
    category = ['3','6','45','48','46','55','49','4','5','7','47']
    category_index = 0


    def parse(self, response):
        detail_list = response.xpath('//ul[@class="newUl clearfix"]/li/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.daetumdesign.com'+i, callback=self.parse_detail)
        page = response.xpath('//div[@class="page"]/ul/li[last()]//text()').extract()[0]
        if self.page < int(page):
            self.page += 1
            yield scrapy.Request('http://www.daetumdesign.com/?anli/Product'+self.category[self.category_index]+'/Index_'+str(self.page)+'.html',callback=self.parse)
        else:
            if self.category_index < 10:
                self.page = 1
                self.category_index += 1
                yield scrapy.Request('http://www.daetumdesign.com/?anli/Product'+self.category[self.category_index]+'/',callback=self.parse)


    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = response.xpath('//*[@id="dqnav"]/a/text()').extract()[0][:-2]
        img_urls = response.xpath('//*[@id="alst"]//img/@src').extract()
        if not img_urls:
            img_urls = response.xpath('//*[@id="sjks"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.daetumdesign.com' + img_urls[i]
        title = response.xpath('//div[@class="infonav3"]/dl/dt/text()').extract()[0]
        title = title.replace('\r\n','').strip()
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        if title == '指甲刀外观设计':
            print(item)
        for key, value in data.items():
            item[key] = value
        yield item
{'img_urls': 'http://www.daetumdesign.com/Up/day_170905/201709051748024306.jpg,http://www.daetumdesign.com/Up/day_170905/201709051748077510.jpg,http://www.daetumdesign.com/Up/day_170905/201709051748112646.jpg,http://www.daetumdesign.com/Up/day_170905/201709051748141592.jpg',
 'sub_title': '指甲刀外观设计',
 'tags': '美容护理设备',
 'title': '指甲刀外观设计',
 'url': 'http://www.daetumdesign.com/?anli/Product5/848.html'}