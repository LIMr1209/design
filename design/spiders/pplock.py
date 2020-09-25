import scrapy
from design.items import DesignItem
import re

data = {
    'channel': 'pplock',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'pplock'
    allowed_domains = ['www.pplock.com']
    page = 1
    start_urls = ['http://www.pplock.com/industrial-design']

    def parse(self, response):
        detail_list = response.xpath('//div[@class="post"]')
        for i in detail_list:
            item = DesignItem()
            url = i.xpath('./div[1]/a/@href').extract()[0]
            title = i.xpath('./div[2]/h2//text()').extract()[0]
            tags = i.xpath('.//div[@class="category"]//text()').extract()
            for i in range(tags.count(' ')):
                tags.remove(' ')
            for i in range(tags.count(', ')):
                tags.remove(', ')
            item['tags'] = tags
            item['url'] = url
            item['title'] = title
            for key, value in data.items():
                item[key] = value

            yield scrapy.Request(url, callback=self.parse_detail, meta={'item': item})

        if self.page < 30:
            self.page += 1
            yield scrapy.Request(url='http://www.pplock.com/industrial-design/page/' + str(self.page),
                                 callback=self.parse)

    def parse_detail(self, response):
        item = response.meta['item']
        img_urls = response.xpath('//div[@class="post-content"]//img/@src').extract()
        remark = response.xpath('//div[@class="post-content"]/p[position()<3]//text()').extract()
        # img_rex = re.compile('-\d+x\d+')
        # for i in range(len(img_urls)):
        #     if img_rex.search(img_urls[i]):
        #         img_urls[i] = img_urls[i].replace(img_rex.findall(img_urls[i])[0],'')
        # print(img_urls)
        if item['title'] == '诺基亚E97概念手机':
            return
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark).strip()
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        # print(item)
        yield item

