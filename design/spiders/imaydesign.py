import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'imaydesign',
    'evt': 3,
    'company': '深圳市怡美工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'imaydesign'
    allowed_domains = ['www.imaydesign.com']
    url = 'http://www.imaydesign.com/case/'
    start_urls = [url]
    page = 1

    def parse(self, response):
        detail_list = response.xpath('//div[@class="cover overlay overlay-hover"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.imaydesign.com'+i, callback=self.parse_detail)
        page = response.xpath('//div[@class="met_pager"]/a[last()-2]/text()').extract()[0]
        if self.page < int(page):
            self.page += 1
            yield scrapy.Request('http://www.imaydesign.com/case/list_3_'+str(self.page)+'.html',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = response.xpath('//ol/a[last()]/text()').extract()[0]
        img_urls = response.xpath('//div[@class="met-editor lazyload clearfix"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.imaydesign.com' + img_urls[i]
        title = response.xpath('//h1/text()').extract()[0]
        item['title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
