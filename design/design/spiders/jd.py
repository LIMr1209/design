# 京东电商
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher
from design.items import ProduceItem
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.Spider):
    name = "jd"
    allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]

    key_words = "保温杯"
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

    def __init__(self):
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
        super(JdSpider, self).__init__()
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )

    def mySpiderCloseHandle(self, spider):
        self.browser.quit()

    def start_requests(self):
        # 1, 3, 5, 7, 9, 11
        for i in [13,15,17,19,21,23,25,27]:
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
        yield item
