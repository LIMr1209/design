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
    'channel': 'newplan',
    'evt': 3,
    'company': '深圳市嘉兰图设计股份有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'newplan'
    allowed_domains = ['www.newplan.com.cn']
    url = 'http://www.newplan.com.cn/index.php/list-4-1.html'
    start_urls = [url]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.EasyDlPipeline': 301,
        }

    }

    # 将chrome初始化放到spider中，成为spider中的元素

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

        # 信号量处理函数：关闭chrome浏览器

    def mySpiderCloseHandle(self, spider):
        self.browser.quit()

    def parse(self, response):
        detail_list = response.xpath('//li[@class="li_4 li_top"]//div[@class="sub"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.newplan.com.cn' + i, callback=self.parse_category, dont_filter=True)

    def parse_category(self, response):
        tags = response.xpath('//div[@class="guide"]/*[last()]/text()').extract()[0]
        detail_list = response.xpath('//ul[@class="pro_list"]/li/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.newplan.com.cn' + i, meta={'usedSelenium': True, 'tags': tags},
                                 callback=self.parse_detail, dont_filter=True)
        try:
            page = response.xpath('//div[@class="page_list"]/*[last()-1]/@href').extract()[0]
            yield scrapy.Request('http://www.newplan.com.cn' + page, callback=self.parse_category, dont_filter=True)
        except:
            pass

    def parse_detail(self, response):

        # print(response.text)
        item = DesignItem()
        url = response.url
        tags = response.meta['tags']
        img_urls = response.xpath('//div[@class="detail detail_p"]/p//img/@src').extract()

        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.newplan.com.cn' + img_urls[i]
        title = response.xpath('//div[@class="guide"]/*[last()]/text()').extract()[0]
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
