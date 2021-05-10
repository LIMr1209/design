# 亚马逊
import json
import logging
import re

import requests
import scrapy
import time

from requests.adapters import HTTPAdapter

from design.items import ProduceItem, TaobaoItem
from pydispatch import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
from design.spiders.selenium import SeleniumSpider


class AmazonCommentSpider(SeleniumSpider):
    name = "amazon_comment"
    # allowed_domains = ["amazon.com"]
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, *args, **kwargs):
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.comment_url = self.setting['OPALUS_GOODS_COMMENT_URL']
        self.comment_data_url = 'https://www.amazon.com/product-reviews/%s?ie=UTF8&reviewerType=all_reviews&formatType=current_format&pageNumber=%s&sortBy=recent'
        self.comment_save_url = self.setting['OPALUS_COMMENT_URL']

        super(AmazonCommentSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.amazon.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        pass

    def comment_save(self,data,out_number):
        success = False
        while not success:
            try:
                res = self.s.post(self.comment_save_url, json=data)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
                # return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            return {'success': False, 'message': message, 'out_number': out_number}
        # 重复爬取
        if 'existence_count' in res.json() and res.json()['existence_count'] == len(data):
            return {'success': True, 'message': '重复爬取', 'out_number': out_number}
        return {'success': True, 'message': ''}

    def comment_end(self, out_number, goods_url):
        comment = {}
        comment['end'] = 1
        comment['good_url'] = goods_url
        try:
            res = self.s.post(self.comment_save_url, data=comment)
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': "终止爬取评论失败", 'out_number': out_number}
        return {'success': True}


    def start_requests(self):
        params = {'category': '烤饼机', 'site_from': 12, 'per_page': 1000}
        res = self.s.get(self.comment_url, params=params, verify=False)
        res = json.loads(res.content)
        goods_data = res['data']
        # url = self.comment_data_url % (goods_data[0]['number'], 1)
        # yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True,
        #                      meta={'usedSelenium': True, 'goods_data': goods_data[0], 'page': 1})
        for i in goods_data:
            page = 1
            url = self.comment_data_url % (i['number'], page)
            yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True,
                                 meta={'usedSelenium': True, 'goods_data': i, 'page': page})

    def parse_detail(self, response):
        goods_data = response.meta['goods_data']
        page = response.meta['page']
        res = self.save_amazon_comment(response,goods_data, page)
        if not res['success']:
            print(res['message'])
            return
        # if res['message'] == '重复爬取':
        #     print("重复爬取 "+goods_data['number'])
        #     return
        if res['message'] == "爬取完成":
            self.comment_end(goods_data['number'], goods_data['url'])
            print("爬取完成 "+goods_data['number'])
            return
        if res['success']:
            page += 1
            url = self.comment_data_url % (goods_data['number'], page)
            yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True,
                                 meta={'usedSelenium': True, 'goods_data': goods_data, 'page': page})


    def save_amazon_comment(self, response,goods_data, page):
        out_number = goods_data['number']
        try:
            data = []
            comment_block = response.xpath('//div[@data-hook="review"]')
            for i in comment_block:
                buyer = i.xpath('.//span[@class="a-profile-name"]/text()').extract()[0]
                score = i.xpath('.//span[@class="a-icon-alt"]/text()').extract()[0].replace(' out of 5 stars','')
                style = ','.join(i.xpath('.//a[@data-hook="format-strip"]/text()').extract())
                first = i.xpath('.//span[@data-hook="review-body"]/span/text()').extract()[0].strip()
                images = i.xpath('.//div[@class="review-image-tile-section"]//img/@src').extract()
                for j in images:
                    j.replace("._SY88",'_SL1600_')
                images = ','.join(images)
                date = i.xpath('.//span[@data-hook="review-date"]/text()').extract()[0].split('on')[1]
                temp = {}
                temp['buyer'] = buyer
                temp['score'] = int(float(score))
                temp['style'] = style
                temp['first'] = first
                temp['images'] = images
                temp['good_url'] = goods_data['url']
                temp['site_from'] = 12
                temp['date'] = date
                data.append(temp)
            if data:
                # data = json.dumps(data, ensure_ascii=False)
                res = self.comment_save(data,goods_data['number'])
                print("保存成功亚马逊", page, out_number)
                return res
            else:
                return {'success': True, 'message': "爬取完成", 'out_number': out_number}
        except Exception as e:
            return {'success': False,
                    'message': "行号 {}, 评论爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e))}
