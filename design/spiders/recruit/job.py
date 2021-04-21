import json
import logging
import copy

import requests
from pydispatch import dispatcher
from scrapy import signals
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider

# 51job
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
        self.key_words =  ['外观设计','平面设计','品牌设计','产品设计','产品工程师','包装设计']
        self.city_code = {
            '杭州': '080200',
            '苏州': '070300',
            '宁波': '080300',
            '丽水': '081000'
        }
        self.city = ["杭州","苏州", '宁波', '丽水']
        self.page = 1
        self.search_url = 'https://search.51job.com/list/%s,000000,0000,00,3,99,%s,2,%s.html'
        self.fail_url = []
        self.opalus_save_url = 'https://opalus.d3ingo.com/api/position/save'
        super(JobSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("");'
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
        urls = []
        while True:
            url = self.search_url%(self.city_code[city], keyword, self.page)
            self.browser.get(url)
            company_names = self.browser.find_elements_by_xpath('//div[@class="er"]/a')
            job_a = self.browser.find_elements_by_xpath('//div[@class="e"]/a[@class="el"]')
            job_names = self.browser.find_elements_by_xpath('//span[@class="jname at"]')
            if not company_names:
                self.page = 1
                break
            for j,i in enumerate(company_names):
                if keyword not in job_names[j].get_attribute('innerText'):
                    continue
                href = job_a[j].get_attribute('href')
                if href.startswith('https://jobs.51job.com'):
                    urls.append(href)
            self.page += 1
        for i in urls:
            is_suc = True
            while is_suc:
                try:
                    self.browser.get(i)
                    is_suc = False
                except:
                    pass
            if '很抱歉，你选择的职位目前已经暂停招聘' in self.browser.page_source:
                continue
            demand_ele = self.browser.find_element_by_xpath('//p[@class="msg ltype"]')
            demand_text = demand_ele.get_attribute('innerText')
            demand_list = demand_text.split('|')
            temp_data = {}
            tags_ele = self.browser.find_elements_by_xpath('//div[@class="jtag"]/div/span')
            tags = []
            for i in tags_ele:
                tags.append(i.get_attribute('innerText'))
            temp_data['tags'] = ','.join(tags)
            temp_data['description'] = self.browser.find_element_by_xpath('//div[@class="bmsg job_msg inbox"]').get_attribute('innerHTML')
            temp_data['title'] = self.browser.find_element_by_xpath('//h1').get_attribute('innerText')
            temp_data['salary'] = self.browser.find_element_by_xpath('//div[@class="cn"]/strong').get_attribute('innerText')
            temp_data['time'] = demand_list[1].strip()
            temp_data['publish_at'] = demand_list[-1].strip()
            temp_data['education'] = demand_list[2].strip()
            company_name = self.browser.find_element_by_xpath('//a[contains(@class,"com_name")]/p').get_attribute('innerText')
            temp_data['company_name'] = company_name
            temp_data['crawl_keyword'] = keyword
            temp_data['crawl_city'] = city
            temp_data['channel'] = '51job'
            temp_data['url'] = self.browser.current_url.split('?')[0]
            temp_data['crawl_user_id'] = 12
            detail_company = {}
            detail_company['companyName'] = company_name
            detail_company['companyUrl'] = self.browser.find_element_by_xpath('//a[contains(@class,"com_name")]').get_attribute('href')
            detail_company['companyDescription'] = self.browser.find_element_by_xpath('//div[@class="tmsg inbox"]').get_attribute('innerText')
            detail_company['industryLevel'] = ','.join([i.get_attribute('innerText') for i in self.browser.find_elements_by_xpath('//div[@class="com_tag"]//a')])
            temp_data['detail_company'] = json.dumps(detail_company)
            res = requests.post(self.opalus_save_url, data=temp_data)
            result = json.loads(res.content)
            if res.status_code != 200 or result['code']:
                logging.error(json.loads(res.content)['message'])
                return
        return True


    def start_requests(self):
        for i in self.key_words:
            for j in self.city:
                flag = self.get_list(i,j)
                if not flag:
                    return
