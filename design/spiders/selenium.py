import random

import scrapy
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from scrapy import signals
from fake_useragent import UserAgent



class SeleniumSpider(scrapy.Spider):

    def __init__(self,*args, **kwargs):
        self.mySetting = get_project_settings()
        self.timeout = self.mySetting['SELENIUM_TIMEOUT']
        self.windowHeight = self.mySetting['WINDOW_HEIGHT']
        self.windowWidth = self.mySetting['windowWidth']
        ua = UserAgent().random
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 无头浏览器
        # 这些网站识别不出来你是用了Selenium，因此需要将模拟浏览器设置为开发者模式
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        # 不加载图片
        # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # ip ua
        # chrome_options.add_argument("--proxy-server=http://tps125.kdlapi.com:15818")
        # chrome_options.add_argument("user-agent={}".format(ua))
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")


        # 初始化chrome对象
        self.browser = webdriver.Chrome(options=chrome_options)

        # self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #           Object.defineProperty(navigator, 'webdriver', {
        #             get: () => undefined
        #           })
        #         """
        # })
        # self.browser.maximize_window()
        # if self.windowHeight and self.windowWidth:
        #     self.browser.set_window_size(900, 900)
        self.browser.set_page_load_timeout(5)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 30)  # 指定元素加载超时时间
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )
        super(SeleniumSpider, self).__init__(*args, **kwargs)


    def mySpiderCloseHandle(self, spider):
        pass
        # self.browser.quit()