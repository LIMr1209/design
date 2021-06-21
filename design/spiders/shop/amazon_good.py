# 亚马逊
import json
import logging
import re

import requests
import scrapy
import time

from requests.adapters import HTTPAdapter
from selenium.common.exceptions import TimeoutException, WebDriverException

from design.items import ProduceItem, TaobaoItem
from pydispatch import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
from design.spiders.selenium import SeleniumSpider
from design.utils.redis_operation import RedisHandle


class AmazonGoodSpider(SeleniumSpider):
    name = "amazon_good"
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
        self.key_words = kwargs['key_words'] if 'key_words' in kwargs else []
        self.page = 1
        self.redis_cli = RedisHandle('localhost', '6379')
        self.list_url = []
        self.error_retry = kwargs['error_retry'] if 'error_retry' in kwargs else 0
        self.fail_url = kwargs['fail_url'] if 'fail_url' in kwargs else []
        self.new_fail_url = []
        self.zh_category = ''
        self.yx_category = ''
        self.get_list_normal = False
        self.suc_count = 0
        # self.max_page = kwargs['max_page']
        # self.max_price_page = 7  # 价格区间的爬10页
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        if not self.error_retry and not self.key_words:
            res = self.s.get(self.setting['OPALUS_GOODS_CATEGORY_URL'])
            result = json.loads(res.content)
            for i in result['data']:
                if i['en_name']:
                    self.key_words.append({
                        'name': i['tags'][0],
                        'value': i['en_name']
                    })
        self.goods_url = self.setting['OPALUS_GOODS_URL']
        # 10041 纽约代码
        self.search_url = 'https://www.amazon.com/s?k=%s&page=%s&qid=1616466294&ref=sr_pg_%s'

        super(AmazonGoodSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.amazon.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('爬取失败')
        logging.error(self.fail_url)
        logging.error('爬取失败')
        logging.error(self.new_fail_url)
        logging.error('待爬取')
        logging.error(self.list_url)
        category = self.zh_category
        price_range = ''
        if self.error_retry:
            if self.list_url:
                for i in self.new_fail_url:
                    if i['name'] == category and i['price_range'] == price_range:
                        i['value'] += self.list_url
                        break
                else:
                    self.new_fail_url.append({'price_range': price_range, 'name': category, 'value': self.list_url})
            if self.fail_url:
                for i in self.fail_url:
                    for j in self.new_fail_url:
                        if i['name'] == j['name'] and i['price_range'] == j['price_range']:
                            j['value'] = list(set(i['value']+j['value']))
                            break
                    else:
                        self.new_fail_url.append(i)
            if self.new_fail_url:
                self.redis_cli.insert('amazon', 'fail_url', json.dumps(self.new_fail_url))
            else:
                self.redis_cli.delete('amazon', 'fail_url')
        else:
            if self.list_url:
                for i in self.fail_url:
                    if i['name'] == category and i['price_range'] == price_range:
                        i['value'] += self.list_url
                        break
                else:
                    self.fail_url.append({'price_range': price_range, 'name': category, 'value': self.list_url})
            if self.fail_url:
                self.redis_cli.insert('amazon', 'fail_url', json.dumps(self.fail_url))
            else:
                self.redis_cli.delete('amazon', 'fail_url')
            if self.get_list_normal and self.key_words:
                self.key_words.pop(0)
            if self.key_words:
                self.redis_cli.insert('amazon', 'keywords', json.dumps(self.key_words))
            else:
                self.redis_cli.delete('amazon', 'keywords')

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

    def get_list_urls(self):
        self.get_list_normal = False
        self.browser_get(self.search_url % (self.yx_category, self.page, self.page))
        time.sleep(2)
        max_page = int(
            self.browser.find_element_by_xpath('//li[@class="a-last"]/preceding-sibling::li[1]').get_attribute(
                'innerText'))
        urls = self.browser.find_elements_by_xpath(
            '//span[@data-component-type="s-product-image"]/../..//a[@class="a-link-normal s-no-outline"]')
        list_urls = []
        for i in urls:
            list_urls.append(i.get_attribute('href'))
        while self.page < max_page:
            self.page += 1
            self.browser_get(self.search_url % (self.yx_category, self.page, self.page))
            time.sleep(2)
            list_url = self.browser.find_elements_by_xpath(
                '//span[@data-component-type="s-product-image"]/../..//a[@class="a-link-normal s-no-outline"]')
            for i in list_url:
                list_urls.append(i.get_attribute('href'))
        self.get_list_normal = True
        return list_urls

    def fail_url_save(self, response):
        if self.error_retry:
            fail_url = self.new_fail_url
        else:
            fail_url = self.fail_url
        name = self.zh_category
        price_range = ''
        for i in fail_url:
            if i['name'] == name and i['price_range'] == price_range:
                if response.url not in i['value']:
                    i['value'].append(response.url)
                break
        else:
            temp = {'name': name, 'value': [response.url], 'price_range': price_range}
            fail_url.append(temp)
        if self.error_retry:
            self.new_fail_url = fail_url
        else:
            self.fail_url = fail_url

    def start_requests(self):
        if self.error_retry:
            if self.fail_url:
                data = self.fail_url.pop(0)
                self.list_url = data['value']
                self.zh_category = data['name']
                self.price_range = data['price_range']
        else:
            self.zh_category = self.key_words[0]['name']
            self.yx_category = self.key_words[0]['value']
            self.list_url = self.get_list_urls()
        yield scrapy.Request(self.list_url[0], callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True})

    def parse_detail(self, response):
        res = self.save_amazon_data(response)
        if not res['success']:
            self.fail_url_save(response)
            logging.error(res['message'])
        else:
            if 'continue' in res and res['continue']:
                pass
            else:
                respon = res['res']
                if respon.status_code != 200 or json.loads(respon.content)['code']:
                    logging.error("产品保存失败" + response.url)
                    logging.error(json.loads(respon.content)['message'])
                    self.fail_url_save(response)
                else:
                    self.suc_count += 1
        self.list_url.pop(0)
        if self.list_url:
            yield scrapy.Request(self.list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True}, dont_filter=True)
        else:
            print(self.fail_url)
            if self.error_retry:
                if self.fail_url:
                    data = self.fail_url.pop(0)
                    self.list_url = data['value']
                    self.zh_category = data['name']
                    self.price_range = data['price_range']
            else:
                self.page = 1
                if self.key_words:
                    self.zh_category = self.key_words[0]['name']
                    self.yx_category = self.key_words[0]['value']
                    self.list_url = self.get_list_urls()
            if self.list_url:
                yield scrapy.Request(self.list_url[0], callback=self.parse_detail, dont_filter=True,
                                     meta={'usedSelenium': True})

    def save_amazon_data(self, response):
        item = TaobaoItem()
        try:
            # height = 0
            # for i in range(height, 2000, 200):
            #     self.browser.execute_script('window.scrollTo(0, {})'.format(i))
            #     time.sleep(0.05)
            title = self.browser.find_element_by_xpath('//span[@id="productTitle"]').get_attribute('innerText').strip()
            brand = self.browser.find_element_by_xpath('//a[@id="bylineInfo"]').get_attribute('innerText')
            try:
                xpath = '//span[@id="priceblock_ourprice" or @id="priceblock_saleprice" or @id="priceblock_dealprice" or @id="priceblock_pospromoprice"]'
                promotion_price = self.browser.find_element_by_xpath(xpath).get_attribute(
                    'innerText')
            except:
                try:
                    promotion_price_text = self.browser.find_element_by_xpath(
                        '//li[@class="swatchSelect"]//span[contains(@class,"a-size-mini")]').get_attribute(
                        'innerText')
                    promotion_price_list = promotion_price_text.split('\n')
                    if len(promotion_price_list) > 1:
                        promotion_price = promotion_price_list[1].strip()
                    else:
                        promotion_price = promotion_price_list[0].strip()
                except:
                    try:
                        promotion_price_text = self.browser.find_element_by_xpath(
                            '//table[@id="HLCXComparisonTable"]//tr[@id="comparison_price_row"]/td[1]//span[@class="a-offscreen"]').get_attribute(
                            'innerText')
                    except:
                        try:
                            promotion_price_text = self.browser.find_element_by_xpath(
                                '//table[@id="HLCXComparisonTable"]//tr[@id="comparison_price_row"]/td[1]/span').get_attribute(
                                'innerText')
                        except:
                            return {'success': True, 'continue': True}
                    promotion_price = promotion_price_text.replace('From ', '')
            try:
                original_price = self.browser.find_element_by_xpath(
                    '//span[@class="priceBlockStrikePriceString a-text-strike"]').get_attribute('innerText')
            except:
                original_price = ''
            try:
                service = self.browser.find_element_by_xpath(
                    '//span[@id="creturns-return-policy-message"]/span').get_attribute('innerText').strip()
            except:
                service = ''
            try:
                comment_text = self.browser.find_element_by_xpath(
                    '//span[@id="acrCustomerReviewText"]').get_attribute('innerText')
            except:
                comment_text = ''
            comment_count = 0
            if comment_text:
                comment_list = re.findall('\d+', comment_text)
                comment_count = ''
                for i in comment_list:
                    comment_count += i
                comment_count = int(comment_count)
            rex = '\{"hiRes":"(.*?)","thumb":'
            img_urls = re.findall(rex, self.browser.page_source)
            if not img_urls:
                rex = ',"large":"(.*?)","main"'
                img_urls = re.findall(rex, self.browser.page_source)
            cover_url = img_urls[0]
            img_urls = ','.join(img_urls)
            detail_keys = self.browser.find_elements_by_xpath(
                '//table[@id="productDetails_detailBullets_sections1"]//th')
            detail_values = self.browser.find_elements_by_xpath(
                '//table[@id="productDetails_detailBullets_sections1"]//td')
            detail_dict = {}
            detail_str_list = []
            for j, i in enumerate(detail_keys):
                if i.get_attribute('innerText') == 'Customer Reviews':
                    continue
                detail_str_list.append(
                    i.get_attribute('innerText') + ':' + detail_values[j].get_attribute('innerText'))
                detail_dict[i.get_attribute('innerText')] = detail_values[j].get_attribute('innerText')
            comment_value_keys = self.browser.find_elements_by_xpath(
                '//div[@class="a-fixed-left-grid-col a-col-left"]//table[@id="histogramTable"]//td[@class="aok-nowrap"]//a')
            comment_value_values = self.browser.find_elements_by_xpath(
                '//div[@class="a-fixed-left-grid-col a-col-left"]//table[@id="histogramTable"]//td[@class="a-text-right a-nowrap"]//a')
            comment_value = {}
            for j, i in enumerate(comment_value_keys):
                comment_value[i.get_attribute('innerText').strip()] = comment_value_values[j].get_attribute(
                    'innerText').strip()
            try:
                comment_value['total'] = self.browser.find_element_by_xpath(
                    '//span[@data-hook="rating-out-of-text"]').get_attribute('innerText')
            except:
                pass
            ele = self.browser.find_element_by_xpath(
                '//div[@class="a-fixed-left-grid-col a-col-left"]//table[@id="histogramTable"]')
            self.browser.execute_script("arguments[0].scrollIntoView();", ele)
            time.sleep(2)
            feature_value_keys = self.browser.find_elements_by_xpath(
                '//div[@id="cr-summarization-attributes-list"]/div//span[@class="a-size-base a-color-base"]')
            feature_value_values = self.browser.find_elements_by_xpath(
                '//div[@id="cr-summarization-attributes-list"]/div//span[@class="a-size-base a-color-tertiary"]')
            feature_value = {}
            for j, i in enumerate(feature_value_keys):
                feature_value[i.get_attribute('innerText').strip()] = feature_value_values[j].get_attribute(
                    'innerText').strip()
            impression = []
            impression_ele = self.browser.find_elements_by_xpath('//span[contains(@id,"cr-lighthouse")]')
            for i in impression_ele:
                impression.append(i.get_attribute('innerText').strip())
            impression = ','.join(impression)
            item['title'] = title
            item['brand'] = brand
            item['original_price'] = original_price
            item['promotion_price'] = promotion_price
            item['service'] = service
            item['comment_count'] = comment_count
            item['brand'] = brand
            item['detail_str'] = ', '.join(detail_str_list)
            item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
            item['comment_value'] = json.dumps(comment_value, ensure_ascii=False)
            item['feature_value'] = json.dumps(feature_value, ensure_ascii=False)
            item['impression'] = impression
            item['site_from'] = 12
            item['site_type'] = 1
            item['cover_url'] = cover_url
            item['img_urls'] = img_urls
            url = self.browser.current_url.split('?')[0].rsplit('/', 1)[0]
            out_number = url.rsplit('/', 1)[1]
            item['url'] = url
            item['out_number'] = out_number
            item['category'] = self.zh_category
            good_data = dict(item)
            print(good_data)
            try:
                res = self.s.post(url=self.goods_url, data=good_data)
            except:
                time.sleep(5)
                res = self.s.post(url=self.goods_url, data=good_data)
            return {'success': True, 'res': res}

        except Exception as e:
            return {'success': False,
                    'message': "行号 {}, 产品爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e))}
