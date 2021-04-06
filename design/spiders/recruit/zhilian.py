# 智联
import json
import logging
import copy
import re

import requests
from pydispatch import dispatcher
from scrapy import signals
from design.items import PositionItem
from design.spiders.selenium import SeleniumSpider


class ZhiLianSpider(SeleniumSpider):
    name = "zhilian"
    allowed_domains = ["sou.zhaopin.com"]

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
            '杭州': '653',
            '苏州': '639',
            '宁波': '654',
            '丽水': '663'
        }
        self.city = ["杭州","苏州", '宁波', '丽水']
        self.page = 1
        self.search_url = 'https://sou.zhaopin.com/?jl=%s&kw=%s&p=%s'
        self.fail_url = []
        self.detail_api = 'https://fe-api.zhaopin.com/c/i/jobs/position-detail-new?number=%s'
        self.opalus_save_url = 'http://127.0.0.1:8002/api/position/save'
        super(ZhiLianSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.zhaopin.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('爬取失败')
        logging.error(self.fail_url)

    def get_data(self,keyword,city):
        list_numbers = []
        while True:
            url = self.search_url % (self.city_code[city], keyword, self.page)
            is_suc = True
            while is_suc:
                try:
                    self.browser.get(url)
                    is_suc = False
                except:
                    pass
            company_names = self.browser.find_elements_by_xpath('//div[@class="iteminfo__line1__compname"]/span')
            job_a = self.browser.find_elements_by_xpath('//div[@class="joblist-box__item clearfix"]')
            if not company_names:
                self.page = 1
                break
            for j, i in enumerate(company_names):
                title = job_a[j].find_element_by_xpath('.//span[@class="iteminfo__line1__jobname__name"]').get_attribute(
                    'innerText')
                if keyword not in title:
                    continue
                url = job_a[j].find_element_by_xpath('.//a[@class="joblist-box__iteminfo iteminfo"]').get_attribute('href')
                number = url.split('?')[0].rsplit('/')[-1].replace('.htm','')
                list_numbers.append(number)
            break
            self.page += 1
        for i in list_numbers:
            is_suc = True
            while is_suc:
                try:
                    self.browser.get(self.detail_api%(i))
                    is_suc = False
                except:
                    pass
            text = re.findall('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">(.*)</pre></body></html>',self.browser.page_source)
            result = json.loads(text[0])
            detail_company = result['data']['detailedCompany']
            detail_position = result['data']['detailedPosition']
            temp_data = {}
            tags = []
            for i in detail_position['welfareLabel']:
                tags.append(i['value'])
            temp_data['tags'] = ','.join(tags)
            temp_data['description'] = detail_position['jobDescPC']
            temp_data['title'] = detail_position['positionName']
            temp_data['salary'] = detail_position['salary60']
            temp_data['contact_name'] = detail_position['staff']['staffName']
            temp_data['time'] = detail_position['workingExp']
            temp_data['publish_at'] = detail_position['publishTime']
            temp_data['education'] = detail_position['education']
            temp_data['company_name'] = detail_position['companyName']
            temp_data['detail_company'] = json.dumps(detail_company)
            temp_data['crawl_keyword'] = keyword
            temp_data['crawl_city'] = city
            temp_data['channel'] = 'zhilian'
            temp_data['url'] = detail_position['positionUrl']
            temp_data['crawl_user_id'] = 12
            res = requests.post(self.opalus_save_url, data=temp_data)
            result = json.loads(res.content)
            if res.status_code != 200 or result['code']:
                logging.error(json.loads(res.content)['message'])
                return



    def start_requests(self):
        for i in self.key_words:
            for j in self.city:
                flag = self.get_data(i,j)
                if not flag:
                    return
