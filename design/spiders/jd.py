# 京东电商
import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JdSpider(SeleniumSpider):
    name = "jd"
    allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]

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
        super(JdSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        # 17,19,21,23,25,27
        for i in [1, 3, 5, 7, 9, 11, 13, 15]:
            self.browser.get(
                "https://search.jd.com/Search?keyword=%s&qrst=1&suggest=1.def.0.V00--38s0&wq=%s&stock=1&page=%d&s=53&click=0" % (
                    self.key_words, self.key_words, i))
            urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
            request_urls = []
            for i in urls:
                request_urls.append(i.get_attribute('href'))
            for url in request_urls:
                yield scrapy.Request(url, callback=self.parse, meta={'usedSelenium': True})

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'http://img10.360buyimg.com/n12/%s' % img_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        item['channel'] = 'jd'
        yield item
