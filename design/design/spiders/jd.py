# 京东电商
import scrapy
from selenium import webdriver
from design.items import ProduceItem
from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.Spider):
    name = "jd"
    allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    key_words = "自拍杆"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
    }

    def start_requests(self):
        browser = webdriver.Chrome(options=self.chrome_options)
        for i in range(1, 8):
            browser.get(
                "https://search.jd.com/Search?keyword=%s&wq=%s&page=%d&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&stock=1&s=61&click=0" % (
                    self.key_words, self.key_words, i))
            urls = browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'http://img10.360buyimg.com/n0/%s' % img_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        yield item
