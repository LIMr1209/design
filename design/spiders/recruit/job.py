# 智联
import json
import logging
import copy

import requests
from pydispatch import dispatcher
from scrapy import signals
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class JobSpider(SeleniumSpider):
    name = "51job"
    allowed_domains = ["www.51job.com"]

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
            '杭州': '080200',
            '苏州': '070300',
            '宁波': '080300',
            '丽水': '081000'
        }
        self.city = ["杭州","苏州", '宁波', '丽水']
        self.page = 1
        self.search_url = 'https://search.51job.com/list/%s,000000,0000,00,9,99,%s,2,%s.html'
        self.fail_url = []
        self.opalus_save_url = 'https://opalus.d3ingo.com/api/company/submit'
        super(JobSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.51job.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('爬取失败')
        logging.error(self.fail_url)

    def get_list(self,keyword,city):
        while True:
            url = self.search_url%(self.city_code[city], keyword, self.page)
            self.browser.get(url)
            company_names = self.browser.find_elements_by_xpath('//div[@class="er"]/a')
            job_names = self.browser.find_elements_by_xpath('//span[@class="jname at"]')
            if not company_names:
                self.page = 1
                break
            for j,i in enumerate(company_names):
                if keyword not in job_names[j].get_attribute('innerText'):
                    continue
                temp_data = {}
                temp_data['name'] = i.get_attribute('innerText')
                temp_data['keywords'] = keyword
                temp_data['craw_city'] = city
                temp_data['soure_url'] = self.browser.current_url
                temp_data['channel'] = '51job'
                temp_data['craw_user_id'] = 3
                temp_data['edit_pattern'] = 0
                res = requests.post(self.opalus_save_url, data=temp_data)
                result = json.loads(res.content)
                if result['code'] != 0 and result['message'] != "公司已存在!":
                    return False
            self.page += 1
        return True


    def start_requests(self):
        for i in self.key_words:
            for j in self.city:
                flag = self.get_list(i,j)
                if not flag:
                    return
