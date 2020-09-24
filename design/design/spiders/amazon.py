# 亚马逊
import scrapy
import time
from design.items import ProduceItem
from pydispatch import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_word = key_words
        self.mySetting = get_project_settings()
        self.timeout = self.mySetting['SELENIUM_TIMEOUT']
        self.isLoadImage = self.mySetting['LOAD_IMAGE']
        self.windowHeight = self.mySetting['WINDOW_HEIGHT']
        self.windowWidth = self.mySetting['windowWidth']
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头浏览器
        # 初始化chrome对象
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        # if self.windowHeight and self.windowWidth:
        #     self.browser.set_window_size(900, 900)
        # self.browser.set_page_load_timeout(self.timeout)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 25)  # 指定元素加载超时时间
        super(AmazonSpider, self).__init__(*args, **kwargs)
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )
    def mySpiderCloseHandle(self, spider):
        self.browser.quit()

    def start_requests(self):
        url = "https://www.amazon.cn/s/ref=sr_pg_%d?rh=i:aps,k:%s&page=%d&keywords=%s&ie=UTF8&qid=%d"
        for page in range(1, 10):
            t = int(time.time())
            yield scrapy.Request(url=url % (page, self.key_word, page, self.key_word, t), callback=self.list_page,meta={'usedSelenium': True})

    def list_page(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//div[@class="a-section aok-relative s-image-square-aspect"]/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('UL320', 'SL1500')
        item['tag'] = self.key_word
        item['img_urls'] = img_urls
        item['channel'] = 'amazon'
        yield item

    # def list_page(self, response):
    #     detail_urls = response.xpath('//div[@data-asin]//a[@class="a-link-normal s-no-outline"]/@href').extract()
    #     for i in detail_urls:
    #         yield scrapy.Request(url='https://www.amazon.cn'+i, callback=self.detail_page,meta={'usedSelenium': True})
    #
    # def detail_page(self, response):
    #     item = ProduceItem()
    #     # img_urls = response.xpath('//li[@class="a-spacing-small item imageThumbnail a-declarative"]//img/@src').extract()
    #     # tags = self.browser.find_element_by_xpath('//ul[@class="a-unordered-list a-nostyle a-horizontal list maintain-height"]').is_displayed()
    #     tags = self.browser.find_elements_by_xpath('//li[@class="a-spacing-small item imageThumbnail a-declarative"]')
    #     img_urls = []
    #     for i in tags:
    #         i.click()
    #         img = self.browser.find_element_by_xpath('//*[@id="imgTagWrapperId"]//img')
    #         img = img.get_attribute('src')
    #         img_urls.append(img)
    #     for i in range(len(img_urls)):
    #         img_urls[i] = img_urls[i].replace('SX679', 'SL1500')
    #     item['tag'] = self.key_word
    #     item['img_urls'] = img_urls
    #     item['channel'] = 'amazon'
    #     yield item