import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'thecool',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'thecoolhunter'
    allowed_domains = ['thecoolhunter.net']
    page = 1
    url = 'https://www.designboom.com/design/page/'+str(page)+'/'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//div[@class="dboom-container-block"]//article')
        for i in detail_list:
            item = DesignItem()
            title = i.xpath('./h3[@class="dboom-title"]/a/text()').extract()[0]
            url = i.xpath('./h3[@class="dboom-title"]/a/@href').extract()[0]
            try:
                remark = i.xpath('./p[@class="dboom-excerpt flip-other"]/text()').extract()[0]
            except:
                remark = ''
            tags = 'design'
            item['title'] = title
            item['remark'] = remark
            item['url'] = url
            item['tags'] = tags
            yield scrapy.Request(url, callback=self.parse_detail, meta={'item': item})
        if self.page < 500:
            print(self.page)
            self.page += 1
            yield scrapy.Request('https://www.designboom.com/design/page' + str(self.page) + '/',
                                 callback=self.parse)

    def parse_detail(self, response):
        print('此详情页的页数', self.page)
        print('*'*50)
        item = response.meta['item']
        try:
            img_url = response.xpath('//img[@class="flip-other"]/@src').extract()[0]
        except:
            try:
                img_url = response.xpath('//div[@class="dboom-article-content"]//img/@src').extract()[0]
            except:
                try:
                    img_url = response.xpath('//img[contains(@class,"alignnone wp-image-")]/@src').extract()[0]
                except:
                    img_url = response.xpath('//img[contains(@class,"alignnone size-full wp-image-")]/@src').extract()[0]
        if not img_url.startswith('https'):
            img_url = 'https://www.designboom.com' + img_url
        item['img_url'] = img_url
        for key, value in data.items():
            item[key] = value
        yield item
