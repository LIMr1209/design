import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class DangdangSpider(SeleniumSpider):
    name = "dangdang"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.page = 1
        super(DangdangSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request("http://search.dangdang.com/?key=%s&act=input" % self.key_words, callback=self.parse_list,
                             meta={'usedSelenium': True})

    def parse_list(self, response):
        request_urls = response.xpath('//ul[@class="bigimg cloth_shoplist"]/li/a/@href').extract()
        for url in request_urls:
            yield scrapy.Request(url, callback=self.parse_detail, meta={'usedSelenium': True})
        page = response.xpath("//ul[@name='Fy']/li[@class='next']/preceding-sibling::li[1]//text()").extract()[0]
        if self.page < int(page):
            print(self.page, page)
            self.page += 1
            yield scrapy.Request(
                "http://search.dangdang.com/?key=%s&act=input&page_index=%s" % (self.key_words, self.page),
                callback=self.parse_list, meta={'usedSelenium': True})

    def parse_detail(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//ul[@id="main-img-slider"]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('x','u')
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        item['channel'] = 'dangdang'
        yield item
