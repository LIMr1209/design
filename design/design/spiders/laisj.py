import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'laisj',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'laisj'
    allowed_domains = ['www.laisj.com']
    page = 1

    def start_requests(self):
        yield scrapy.FormRequest(
            url='http://www.laisj.com/publics2/work/list',
            formdata={'page': str(self.page)},
            callback=self.parse
        )

    def parse(self, response):
        content = json.loads(response.text)
        detail_list = content['data']
        for i in detail_list:
            url = i['url']
            yield scrapy.Request('http://www.laisj.com' + url, callback=self.parse_detail)
        last_page = content['last_page']
        if self.page < int(last_page):
            self.page += 1
            yield scrapy.FormRequest(
                url='http://www.laisj.com/publics2/work/list',
                formdata={'page': str(self.page)},
                callback=self.parse
            )

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//div[@class="content-other"]//img/@src').extract()
        title = response.xpath('//div[@class="content-table"]/div[1]/div[1]/div/text()').extract()[0]
        company = response.xpath('//div[@class="info-name"]/text()').extract()[0]
        tags = []
        try:
            tag1 = response.xpath('//div[@class="content-table"]/div[1]/div[2]/div/text()').extract()[0]
        except:
            pass
        else:
            tags.append(tag1)
        try:
            tag2 = response.xpath('//div[@class="content-label"]/a/text()').extract()
            for i in range(len(tag2)):
                tag2[i] = tag2[i].strip().replace('、', '')
        except:
            pass
        else:
            tags.extend(tag2)
        tags = ','.join(tags)
        item['url'] = url
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['company'] = company
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value

        yield item
