# 智联
import json
import logging
import copy

import requests
from pydispatch import dispatcher
from scrapy import signals
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class BossSpider(SeleniumSpider):
    name = "boss"
    allowed_domains = ["www.zhipin.com"]

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

    def __init__(self, *args, **kwargs):
        # 工业设计、结构设计、外观设计、平面设计、品牌设计、产品设计、产品工程师、包装设计
        self.key_words =  ['工业设计','结构设计','外观设计','平面设计','品牌设计','产品设计','产品工程师','包装设计']
        self.city_code = {
            '杭州': '101210100',
            '苏州': '101190400',
            '宁波': '101210400',
            '丽水': '101210800'
        }
        self.city = ["杭州","苏州", '宁波', '丽水']
        self.page = 1
        self.search_url = 'https://www.zhipin.com/c%s/?query=%s&page=%s&ka=page-%s'
        self.fail_url = []
        self.opalus_save_url = 'http://opalus-dev.taihuoniao.com/api/company/submit'
        super(BossSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.zhipin.com");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口
        self.start_requests()

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('爬取失败')
        logging.error(self.fail_url)

    def get_list(self,keyword,city):
        company_url = []
        while True:
            url = self.search_url%(self.city_code[city], keyword, self.page, self.page)
            self.browser.get(url)
            company_names_a = self.browser.find_elements_by_xpath('//div[@class="company-text"]/h3/a')
            job_names = self.browser.find_elements_by_xpath('//span[@class="job-name"]/a')
            if not company_names_a:
                self.page = 1
                break
            for j,i in enumerate(company_names_a):
                if keyword not in job_names[j].get_attribute('innerText'):
                    continue
                company_url.append(i.get_attribute('src'))
            self.page += 1
        for i in company_url:
            self.browser.get(i)
            temp_data = {}
            temp_data['name'] = self.browser.find_element_by_xpath('//div[@class="job-sec company-business"]/h4').get_attribute('innerText')
            temp_data['keywords'] = keyword
            temp_data['craw_city'] = city
            temp_data['soure_url'] = self.browser.current_url
            temp_data['channel'] = 'boss'
            temp_data['craw_user_id'] = 3
            temp_data['edit_pattern'] = 0
            res = requests.post(self.opalus_save_url, data=temp_data)
            result = json.loads(res.content)
            if result['code'] != 0:
                return False
        return True


    def start_requests(self):
        for i in self.key_words:
            for j in self.city:
                flag = self.get_list(i,j)
                if not flag:
                    return
