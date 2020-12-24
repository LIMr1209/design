import json
import os
import time
import scrapy
from pymongo import MongoClient
from design.spiders.selenium import SeleniumSpider
import copy


class TaobaoSpider(SeleniumSpider):
    name = "taobao_list"
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': 'log/%s.log' % name
    }
    max_page = 10
    list_url = []

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.price_range = ""
        self.page = 10
        self.data_url = 'https://s.taobao.com/search?q={name}&filter=reserve_price{price_range}&s={page_count}'
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.browser.switch_to_window('window.open()')  # 切换新窗口
        self.browser.get('https://www.taobao.com/')

    # 更换登陆信息
    def update_cookie(self):
        self.browser.delete_all_cookies()  # 删除cookie
        login_url = 'https://login.taobao.com/member/login.jhtml'
        username = '斌爷爷1058169464'
        password = 'limr1209'
        cookie_file = os.path.join('tmp', '{}@{}.cookie'.format(username, self.name))
        if not os.path.exists(cookie_file):
            self.browser.get(login_url)
            self.browser.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
            self.browser.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
            self.browser.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
            cookies = self.browser.get_cookies()
            # fw = open(cookie_file, 'w')
            # fw.write(json.dumps(cookies))
            # fw.close()
        else:
            fr = open(cookie_file, 'r')
            cookies = json.loads(fr.read())
            fr.close()
            for i in cookies:
                self.browser.add_cookie(i)
        time.sleep(2)

    def start_requests(self):
        # self.update_cookie()
        page_count = str((self.page) * 44)
        url = self.data_url.format(name=self.key_words, price_range=self.price_range, page_count=page_count)
        yield scrapy.Request(url, meta={'usedSelenium': True, "page": self.page}, callback=self.parse_list)

    def parse_list(self, response):
        time.sleep(10)
        # ele = self.browser.find_element_by_xpath('//div[@class="inner clearfix"]')
        # self.browser.execute_script("arguments[0].scrollIntoView();", ele)
        list_url = response.xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a/@href').extract()
        list_cover_url = response.xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a/img/@data-src').extract()

        mc = MongoClient("127.0.0.1", 27017)
        test_db = mc["test"]
        tmp = self.price_range.replace('[', '').replace(']', '').split(',')
        if len(tmp) == 1:
            price_page = tmp[0]+'以上'
        else:
            price_page = tmp[0]+'-'+tmp[1]
        data = {
            'page': self.page,
            'price_range': price_page,
            'key_words': self.key_words,
            'is_suc': 0
        }
        for j,i in enumerate(list_url):
            temp = copy.deepcopy(data)
            temp['link'] = i
            temp['cover_url'] = 'https:'+list_cover_url[j]
            test_db.taobao.insert(temp)
        if self.page < self.max_page:
            page_count = str((self.page) * 44)
            self.page += 1
            url = self.data_url.format(name=self.key_words, price_range=self.price_range, page_count=page_count)
            yield scrapy.Request(url, meta={'usedSelenium': True}, callback=self.parse_list)
