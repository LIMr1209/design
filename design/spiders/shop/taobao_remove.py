import json
import requests
import scrapy
from pydispatch import dispatcher
from requests.adapters import HTTPAdapter
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException, WebDriverException
from design.spiders.selenium import SeleniumSpider



class TaobaoSpider(SeleniumSpider):
    name = "taobao_remove"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, *args, **kwargs):
        self.page = 1
        self.list_url = []
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.goods_list_url = self.setting['OPALUS_GOODS_LIST_URL']
        self.goods_remove_url = self.setting['OPALUS_GOODS_REMOVE_URL']
        kwargs['time_out'] = 2
        kwargs['se_port'] = 9222

        super(TaobaoSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.taobao.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        pass

    def browser_get(self, url):
        try:
            self.browser.get(url)
        except TimeoutException as e:
            self.browser_get(url)
        except WebDriverException as e:
            try:
                self.browser.execute_script('window.stop()')
            except Exception as e:
                pass
            self.browser_get(url)

    def start_requests(self):
        self.list_url = self.get_list_urls()  # 获取商品链接
        yield scrapy.Request(self.list_url[0]['url'], callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True})

    def get_list_urls(self):
        params = {'site_from':8, 'per_page':100, 'page': self.page}
        res = self.s.get(self.goods_list_url, params=params)
        data = json.loads(res.content)['data']
        self.page += 1
        return data

    def parse_detail(self, response):
        res = {}
        if "detail.tmall.com" in self.browser.current_url:
            if "此商品已下架" in self.browser.page_source:
                self.s.get(self.goods_remove_url, params={'id':self.list_url[0]['id']})
                return {'success': True, 'message': '此商品已下架'}
            if '起拍价格' in self.browser.page_source:
                self.s.get(self.goods_remove_url, params={'id': self.list_url[0]['id']})
            if '很抱歉，您查看的商品找不到了！' in self.browser.page_source:
                self.s.get(self.goods_remove_url, params={'id': self.list_url[0]['id']})

        if "item.taobao.com" in self.browser.current_url:
            if "很抱歉，您查看的宝贝不存在，可能已下架或者被转移。" in self.browser.page_source:
                self.s.get(self.goods_remove_url, params={'id':self.list_url[0]['id']})
        self.list_url.pop(0)
        if self.list_url:
            yield scrapy.Request(self.list_url[0]['url'], callback=self.parse_detail,
                                 meta={'usedSelenium': True}, dont_filter=True, )
        else:
            self.list_url = self.get_list_urls()
            yield scrapy.Request(self.list_url[0]['url'], callback=self.parse_detail, dont_filter=True,
                                 meta={'usedSelenium': True})


