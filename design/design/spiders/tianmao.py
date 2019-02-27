# 天猫
import scrapy
from selenium import webdriver
from design.items import ProduceItem
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
# scrapy 信号相关库
from scrapy import signals
from pydispatch import dispatcher


class JdSpider(scrapy.Spider):
    name = "tianmao"
    key_words = "空气净化器"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.SeleniumMiddleware': 543,
            # 将scrapy默认的user-agent中间件关闭
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    def __init__(self, timeout=30, isLoadImage=False, windowHeight=None, windowWidth=None):
        # 从settings.py中获取设置参数
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头浏览器
        # 初始化chrome对象
        self.browser = webdriver.Chrome(options=chrome_options)
        # self.browser.set_page_load_timeout(self.timeout)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 25)  # 指定元素加载超时时间
        super(JdSpider, self).__init__()
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )

        # 信号量处理函数：关闭chrome浏览器

    def mySpiderCloseHandle(self, spider):
        self.browser.quit()

    def start_requests(self):
        for i in range(1):
            s = i * 60
            yield scrapy.Request(
                "https://list.tmall.com/search_product.htm?q=%s&s=%s&type=p&vmarket=&spm=875.7931836/B.a2227oh.d100&from=mallfp..pc_1_searchbutton" % (
                    self.key_words, s), callback=self.parse_list, meta={'usedSelenium': True})

    def parse_list(self, response):
        urls = response.xpath('//div[@class="productImg-wrap"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request('https:' + url, callback=self.parse_detail, meta={'usedSelenium': True})

    def parse_detail(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//ul[@id="J_UlThumb"]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('_60x60q90.jpg', '')
            if not img_urls[i].startswith('https'):
                img_urls[i] = 'https:' + img_urls[i]
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        # print(item)
        yield item
