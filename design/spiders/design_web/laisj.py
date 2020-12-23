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
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0',
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES':{
            'design.middlewares.UserAgentSpiderMiddleware': 300,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 300
        },
    }
    # start_urls = ['http://www.laisj.com/publics2/work/list']

    def start_requests(self):
        yield scrapy.Request(
            url='http://www.laisj.com/publics2/work/list',
            callback=self.parse,
            headers=self.headers
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
            yield scrapy.Request(
                url='http://www.laisj.com/publics2/work/list?page=%s'% str(self.page),
                callback=self.parse
            )

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//div[@class="content-other"]//img/@src').extract()
        title = response.xpath('//label[text()="案例名称 "]/../div/text()').extract()[0]
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
        try:
            material_tags = response.xpath('//label[text()="主要材质 "]/../div/text()').extract()[0]
        except:
            material_tags = ''
        tags = ','.join(tags)
        item['url'] = url
        item['title'] = title
        item['sub_title'] = title
        item['material_tags'] = material_tags
        item['img_urls'] = ','.join(img_urls)
        item['company'] = company
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value

        yield item
