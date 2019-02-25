import scrapy
from design.items import DesignItem
import re

data = {
    'channel': 'sj33',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'sj33'
    allowed_domains = ['www.sj33.cn']
    page = 1
    start_urls = ['http://www.sj33.cn/industry/']

    def parse(self, response):
        detail_list = response.xpath('//ul[@class="imglist2"]/li/div[1]/a[1]/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.sj33.cn'+i, callback=self.parse_detail)

        if self.page < 35:
            self.page += 1
            yield scrapy.Request(url='http://www.sj33.cn/industry/P'+str(self.page)+'.html',callback=self.parse)


    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//div[@class="artcon"]//img/@src').extract()
        tags = response.xpath('//div[@id="loat6"]/a/text()').extract()
        try:
            tags[0] = response.xpath('//div[@class="zuozhe1"]/a/text()').extract()[0]
        except:
            tags.pop(0)
        tags = ','.join(tags)
        title = response.xpath('//h1/text()').extract()[0]
        remark = response.xpath('//div[@class="articlebox"]/div[@class="artcon"]//text()').extract()
        # remark = ''.join(response.xpath('//div[@class="artcon"]/p[1]//text()').extract()).strip()
        # if not remark:
        #     remark = ''.join(response.xpath('//div[@class="artcon"]/p[2]//text()').extract()).strip()
        # if not remark:
        #     remark = response.xpath('//div[@class="artcon"]/text()').extract()[0]
        remark = [''.join(i.split())for i in remark]
        remark = ''.join(remark)
        if len(remark) > 480:
            remark = remark[:480]
        item['tags'] = tags
        item['sub_title'] = title
        item['title'] = title.strip()
        item['remark'] = remark.strip()
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        print(item)
        for key, value in data.items():
            item[key] = value
        yield item
