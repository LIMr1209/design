import json
import logging
import copy
import time

import requests
from pydispatch import dispatcher
from scrapy import signals
from selenium.common.exceptions import TimeoutException
import datetime
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider
import re


# boss
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
        self.key_words = ['平面设计', '品牌设计', '产品设计', '产品工程师', '包装设计']
        self.city_code = {
            '杭州': '101210100',
            '苏州': '101190400',
            '宁波': '101210400',
            '丽水': '101210800'
        }
        self.city = ['宁波','丽水']
        self.page = 1
        self.search_url = 'https://www.zhipin.com/c%s/?query=%s&page=%s&ka=page-%s'
        self.fail_url = []
        self.opalus_save_url = 'https://opalus.d3ingo.com/api/position/save'
        super(BossSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.zhipin.com");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('爬取失败')
        logging.error(self.fail_url)

    def get_url(self, url):
        is_suc = True
        while is_suc:
            try:
                self.browser.get(url)
                is_suc = False
            except:
                pass
        time.sleep(2)

    def get_list(self, keyword, city):
        urls = []
        publish_at_list = []
        while True:
            url = self.search_url % (self.city_code[city], keyword, self.page, self.page)
            self.get_url(url)
            job_names = self.browser.find_elements_by_xpath('//span[@class="job-name"]/a')
            publish_at_ele = self.browser.find_elements_by_xpath('//span[@class="job-pub-time"]')
            if not job_names:
                self.page = 1
                break
            for j, i in enumerate(job_names):
                if keyword not in i.get_attribute('innerText'):
                    continue
                href = i.get_attribute('href')
                if href != "javascript:;":
                    publish_at = publish_at_ele[j].get_attribute('innerText').replace('发布于', '')
                    if publish_at == '昨天':
                        publish_at = (datetime.datetime.now() + datetime.timedelta(days=-1)).date().strftime(
                            '%m{m}%d{d}').format(m='月', d='日')
                    publish_at_list.append(publish_at)
                    urls.append(i.get_attribute('href'))
            self.page += 1
        for j, i in enumerate(urls):
            self.get_url(i)
            temp_data = {}
            demand_ele = self.browser.find_element_by_xpath(
                '//div[@class="job-banner"]//div[@class="info-primary"]/div[@class="name"]/following-sibling::p[1]')
            demand_html = demand_ele.get_attribute('innerHTML')
            demand_list = re.findall('</em>(.*)', demand_html)[0].split('<em class="dolt"></em>')
            tags_ele = self.browser.find_elements_by_xpath('//div[@class="job-banner"]//div[@class="job-tags"]/span')
            tags = []
            for i in tags_ele:
                tags.append(i.get_attribute('innerText'))
            temp_data['tags'] = ','.join(tags)
            temp_data['description'] = self.browser.find_element_by_xpath(
                '//div[@class="job-sec"]/div[@class="text"]').get_attribute('innerHTML')
            temp_data['title'] = self.browser.find_element_by_xpath('//div[@class="name"]/h1').get_attribute(
                'innerText')
            temp_data['salary'] = self.browser.find_element_by_xpath(
                '//div[@class="name"]/span[@class="salary"]').get_attribute(
                'innerText')
            temp_data['time'] = demand_list[0].strip()
            temp_data['publish_at'] = publish_at_list[j]
            temp_data['education'] = demand_list[1].strip()
            try:
                temp_data['contact_name'] = self.browser.find_element_by_xpath('//div[@class="detail-op"]//h2[@class="name"]').get_attribute('innerText')
            except:
                temp_data['contact_name'] = ''
            try:
                company_name = self.browser.find_element_by_xpath(
                    '//div[@class="job-sec"]/div[@class="name"]').get_attribute(
                    'innerText')
            except:
                try:
                    company_name = self.browser.find_element_by_xpath(
                        '//a[@ka="job-detail-company_custompage"]').get_attribute('innerText').strip()
                except:
                    continue
            temp_data['company_name'] = company_name
            temp_data['crawl_keyword'] = keyword
            temp_data['crawl_city'] = city
            temp_data['channel'] = 'boss'
            temp_data['url'] = self.browser.current_url.split('?')[0]
            temp_data['crawl_user_id'] = 12
            company_a = self.browser.find_element_by_xpath('//div[@class="company-info"]/a')
            company_url = company_a.get_attribute('href')
            self.get_url(company_url)
            detail_company = {}
            detail_company['companyName'] = company_name
            detail_company['companyUrl'] = company_url
            try:
                detail_company['companyDescription'] = self.browser.find_element_by_xpath(
                    '//div[@class="job-sec"]/div[@class="text fold-text"]').get_attribute('innerText')
            except:
                detail_company['companyDescription'] = ''
            temp_data['detail_company'] = json.dumps(detail_company)
            res = requests.post(self.opalus_save_url, data=temp_data)
            result = json.loads(res.content)
            if result['code'] != 0 and result['message'] != "公司已存在!":
                return False
        return True

    def start_requests(self):
            for x, i in enumerate(self.key_words):
                if x != 0:
                    self.city = ["杭州", "苏州", '宁波', '丽水']
                for j in self.city:
                    try:
                        flag = self.get_list(i, j)
                        if not flag:
                            return
                    except:
                        print(i,j)
