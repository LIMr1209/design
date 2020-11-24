import scrapy
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from scrapy import signals

class SeleniumSpider(scrapy.Spider):

    def __init__(self,*args, **kwargs):
        self.mySetting = get_project_settings()
        self.timeout = self.mySetting['SELENIUM_TIMEOUT']
        self.isLoadImage = self.mySetting['LOAD_IMAGE']
        self.windowHeight = self.mySetting['WINDOW_HEIGHT']
        self.windowWidth = self.mySetting['windowWidth']
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头浏览器
        # 初始化chrome对象
        self.browser = webdriver.Chrome(options=chrome_options)
        # self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        # if self.windowHeight and self.windowWidth:
        #     self.browser.set_window_size(900, 900)
        # self.browser.set_page_load_timeout(self.timeout)  # 页面加载超时时间
        self.wait = WebDriverWait(self.browser, 25)  # 指定元素加载超时时间
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )
        super(SeleniumSpider, self).__init__(*args, **kwargs)


    def mySpiderCloseHandle(self, spider):
        # pass
        self.browser.quit()