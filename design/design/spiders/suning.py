# 苏宁
import scrapy
from design.items import ProduceItem


class SNSpider(scrapy.Spider):
    name = "suning"
    key_words = "钢笔"
    cp = 0
    paging = 0
    # url 关键词 变化 url 变化
    url = 'https://search.suning.com/emall/searchV1Product.do?keyword=%s&ci=0&pg=01&cp=%s&il=0&st=0&iy=0&isNoResult=0&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=010&paging=%s&sub=1&jzq=20895'
    start_urls = [url % (key_words, cp, paging)]
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
    }

    def parse(self, response):
        detail_urls = response.xpath('//li//div[@class="title-selling-point"]/a/@href').extract()
        for i in range(len(detail_urls)):
            if not detail_urls[i].startswith('https'):
                detail_urls[i] = 'https:' + detail_urls[i]
        for url in detail_urls:
            yield scrapy.Request(url, callback=self.parse_detail, )
        if self.paging < 3:
            self.paging += 1
            yield scrapy.Request(self.url % (self.key_words, self.cp, self.paging))
        else:
            if self.cp < 2:
                self.paging = 0
                self.cp += 1
                yield scrapy.Request(self.url % (self.key_words, self.cp, self.paging))

    def parse_detail(self, response):
        item = ProduceItem()
        image_urls = response.xpath('//div[@class="imgzoom-thumb-main"]//img/@src').extract()
        for i in range(len(image_urls)):
            image_urls[i] = image_urls[i].replace('60w_60h', '800w_800h')
            image_urls[i] = image_urls[i].replace('75w_100h', '800w_800h')
            if not image_urls[i].startswith('http'):
                image_urls[i] = 'http:' + image_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = image_urls
        yield item
