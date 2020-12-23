import scrapy
from design.items import DesignItem
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
# scrapy 信号相关库
from scrapy import signals
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher

data = {
    'channel': 'leadhh',
    'evt': 3,
    'company':'北京乐品乐道科技有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'leadhh'
    allowed_domains = ['www.leadhh.com']
    start_urls = ['http://www.leadhh.com/cases/cases.html']
    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.SeleniumMiddleware': 543,
            # 将scrapy默认的user-agent中间件关闭
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    def __init__(self, timeout=30, isLoadImage=True, windowHeight=None, windowWidth=None):
        # 从settings.py中获取设置参数
        self.mySetting = get_project_settings()
        self.timeout = self.mySetting['SELENIUM_TIMEOUT']
        self.isLoadImage = self.mySetting['LOAD_IMAGE']
        self.windowHeight = self.mySetting['WINDOW_HEIGHT']
        self.windowWidth = self.mySetting['windowWidth']
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头浏览器
        # 初始化chrome对象
        self.browser = webdriver.Chrome()
        if self.windowHeight and self.windowWidth:
            self.browser.set_window_size(900, 900)
        # self.browser.set_page_load_timeout(self.timeout)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 25)  # 指定元素加载超时时间
        super(DesignCaseSpider, self).__init__()
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )
    def mySpiderCloseHandle(self, spider):
        self.browser.quit()


    def parse(self, response):
        detail_list = response.xpath('//div[@class="mc2_list clearfix"]/ul/li/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.leadhh.com'+i, callback=self.parse_detail,meta={'usedSelenium': True})


    def parse_detail(self, response):
        img_urls = response.xpath('//div[@id="ctl00_ContentPlaceHolder1_caseInfo"]//img/@src').extract()
        img_urls = ['http://www.leadhh.com'+i for i in img_urls]
        img_urls = ','.join(img_urls)

        item = DesignItem()
        url = response.url
        try:
            tags = response.xpath('//a[contains(@class,"m2menu_cuta")]/text()').extract()[0]
        except:
            tags = ''
        title = response.xpath('//div[@class="m2pos"]/text()').extract()[0]
        try:
            remark = response.xpath('//div[@id="ctl00_ContentPlaceHolder1_caseInfo"]//span/text()').extract()
            remark = ','.join(remark).strip()
        except:
            remark = ''
        item['tags'] = tags
        item['title'] = title.strip()
        item['remark'] = remark.strip()
        item['url'] = url
        item['img_urls'] = img_urls
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
