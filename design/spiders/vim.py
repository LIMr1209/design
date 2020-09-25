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
    'channel': 'vim',
    'evt': 3,
    'company': '上海威曼工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'vim'
    allowed_domains = ['www.vimdesign.com']
    start_urls = ['http://www.vimdesign.com/products.asp?clsid=669&cid=669']
    cookie = {
        'ASPSESSIONIDSARRCRBT': 'BFFGGCODPJLIDDOBECDDMBMG',
        'Hm_lvt_4ae866d3970aed50c66cf19ed4f3e455': '1544608879',
        'ASPSESSIONIDCQQSDQAR': ' ELIPEPKABBIIBMHAIILMDECF',
        'Hm_lpvt_4ae866d3970aed50c66cf19ed4f3e455': '1544670048',
    }

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
        self.browser = webdriver.Chrome(options=chrome_options)
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
        detail_list = response.xpath('//a[@class="cpmainatxt"]')
        for i in detail_list:
            url = i.xpath('./@href').extract()[0]
            # title = i.xpath('./p[1]/text()').extract()[0].split('|')[1].strip()
            # tags = i.xpath('./p[2]/text()').extract()[0]
            # print(tags, title)
            yield scrapy.Request('http://www.vimdesign.com/' + url,cookies=self.cookie, callback=self.parse_detail,meta={'usedSelenium': True,})

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = response.xpath('//div[@class="leibie2"]/a[4]/text()').extract()[0]

        title = response.xpath('//div[@class="leibie2"]/a[3]/text()').extract()[0]
        img_urls = response.xpath('//div[@class="hidden-l tupian"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http://www.vimdesign.com/'):
                img_urls[i] = 'http://www.vimdesign.com/' + img_urls[i]
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
        # print(item)
