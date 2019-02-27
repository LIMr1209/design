# 唯品会
import scrapy
from selenium import webdriver
from design.items import ProduceItem

from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.Spider):
    name = "weiping"
    key_words = "路由器"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
    }

    def start_requests(self):
        browser = webdriver.Chrome(options=self.chrome_options)
        for i in range(1, 3):
            browser.get(
                "https://category.vip.com/suggest.php?keyword=%s&page=%s" % (
                    self.key_words, i))
            urls = browser.find_elements_by_xpath('//div[@class="goods-image"]/a')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)

    def parse(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[@id="J-sImg-wrap"]/div[position()>1]/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('64x64', '420x420')
            if not img_urls[i].startswith('https'):
                img_urls[i] = 'https://' + img_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        yield item
