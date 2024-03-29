# 京东电商
import asyncio
import json
import logging
import random
import re
import time
import requests
import scrapy
from fake_useragent import UserAgent
from pydispatch import dispatcher
from requests.adapters import HTTPAdapter
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException, WebDriverException

from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider
import urllib3

from design.utils.pyppeteer_code import jd_code
from design.utils.redis_operation import RedisHandle

urllib3.disable_warnings()


class JdSpider(SeleniumSpider):
    name = "jd_good"
    # allowed_domains = ["search.jd.com"]
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, *args, **kwargs):
        self.page = kwargs['page'] if 'page' in kwargs else 1
        # if 'price_range_list' in kwargs and kwargs['price_range_list']:
        #     self.price_range_list = kwargs['price_range_list']
        # else:
        #     self.price_range_list = {
        #         # '吹风机': ['459-750', '751-999', '1000gt'],
        #         # '真无线蓝牙耳机 降噪 入耳式': ['300-900', '900-3000'],
        #     }
        self.redis_cli = RedisHandle('127.0.0.1', '6379')
        self.list_url = []
        self.error_retry = kwargs['error_retry'] if 'error_retry' in kwargs else 0
        self.fail_url = kwargs['fail_url'] if 'fail_url' in kwargs else []
        self.new_fail_url = []
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.jd_account_list = []
        if len(self.setting['JD_ACCOUNT_LIST']) != len(self.setting['JD_PASSWORD_LIST']):
            logging.error('JD用户信息长度不匹配')
            return
        for i, j in enumerate(self.setting['JD_ACCOUNT_LIST']):
            self.jd_account_list.append({
                'account': j,
                'password': self.setting['JD_PASSWORD_LIST'][i]
            })
        self.goods_url = self.setting['OPALUS_GOODS_URL']
        self.opalus_goods_tags_url = self.setting['OPALUS_GOODS_TAGS_URL']
        self.search_url = 'https://search.jd.com/Search?keyword={name}&page={page}&s=53&ev=^exprice_{price_range}^'
        self.comment_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
        self.suc_count = 0
        self.comment_no_count = 0
        self.redis_key = {'name': 'jd'}

        if 'kind' in kwargs:
            if kwargs['kind'] == 2:
                self.redis_key = {'name': 'jd_custom'}

        if 'key_words_str' not in kwargs:
            if self.error_retry:
                self.key_words = []
            else:
                self.key_words = self.get_opalus_goods_tags()
        else:
            self.key_words = json.loads(kwargs['key_words_str'])

        super(JdSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        js = 'window.open("https://www.jd.com/");'
        self.browser.execute_script(js)
        self.browser.close()
        self.browser.switch_to_window(self.browser.window_handles[0])
        # old_num = len(self.browser.window_handles)
        # self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def get_opalus_goods_tags(self):
        response = self.s.get(self.opalus_goods_tags_url, params={'site_from':9})
        result = json.loads(response.content)
        return result['data']

    def fail_url_save(self, response):
        if self.error_retry:
            fail_url = self.new_fail_url
        else:
            fail_url = self.fail_url
        name = self.get_category()
        # price_range = self.get_price_range()
        for i in fail_url:
            # if i['name'] == name and i['price_range'] == price_range:
            if i['name'] == name:
                if response.url not in i['value']:
                    i['value'].append(response.url)
                break
        else:
            # temp = {'name': name, 'value': [response.url], 'price_range': price_range}
            temp = {'name': name, 'value': [response.url]}
            fail_url.append(temp)
        if self.error_retry:
            self.new_fail_url = fail_url
        else:
            self.fail_url = fail_url

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('价位档')
        # logging.error(self.price_range_list)
        logging.error('爬取失败')
        logging.error(self.fail_url)
        if self.error_retry:
            if self.fail_url:
                for i in self.fail_url:
                    for j in self.new_fail_url:
                        # if i['name'] == j['name'] and i['price_range'] == j['price_range']:
                        if i['name'] == j['name']:
                            j['value'] = list(set(i['value'] + j['value']))
                            break
                    else:
                        self.new_fail_url.append(i)
            if self.new_fail_url:
                self.redis_cli.insert(self.redis_key['name'], 'fail_url', json.dumps(self.new_fail_url))
            else:
                self.redis_cli.delete(self.redis_key['name'], 'fail_url')
        else:
            if self.page != self.max_page or self.page != 1:
                self.redis_cli.insert(self.redis_key['name'], 'page', self.page)
            else:
                self.redis_cli.delete(self.redis_key['name'], 'page')
            if self.page == self.max_page:
                # if self.category in self.price_range_list and len(self.price_range_list[self.category]) > 1:
                #     self.price_range_list[self.category].pop(0)
                # else:
                self.key_words.pop(0)
            if self.key_words:
                # self.redis_cli.insert('taobao', 'price_range_list', json.dumps(self.price_range_list))
                self.redis_cli.insert(self.redis_key['name'], 'keywords', json.dumps(self.key_words))
            else:
                self.redis_cli.delete(self.redis_key['name'], 'keywords')
            if self.fail_url:
                self.redis_cli.insert(self.redis_key['name'], 'fail_url', json.dumps(self.fail_url))
            else:
                self.redis_cli.delete(self.redis_key['name'], 'fail_url')

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
        if self.error_retry:
            data = self.fail_url.pop(0)
            self.list_url = data['value']
            self.category = data['name']
            # self.price_range = data['price_range']
        else:
            self.category = self.key_words[0]['name']
            self.max_page = self.key_words[0]['max_page']
            self.list_url = self.get_list_urls()
        yield scrapy.Request(self.list_url[0], callback=self.parse_detail,
                             meta={'usedSelenium': True}, dont_filter=True)

    def get_list_urls(self):
        list_url = []
        # if self.category in self.price_range_list:
        #     url = self.search_url.format(name=self.category,
        #                                  price_range=self.price_range_list[self.key_words[0]['name']][0], page=self.page)
        # else:
        url = self.search_url.format(name=self.category, price_range='', page=self.page)
        self.browser_get(url)
        time.sleep(3)
        urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
        for i in urls:
            if 'https://ccc-x.jd.com' in i.get_attribute('href'):
                continue
            list_url.append(i.get_attribute('href'))
        if not list_url:
            self.browser.refresh()
        urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
        for i in urls:
            if 'https://ccc-x.jd.com' in i.get_attribute('href'):
                continue
            list_url.append(i.get_attribute('href'))
        return list_url

    def detail_data(self, response):
        item = TaobaoItem()
        try:
            # height = 0
            # for i in range(height, 800, 200):
            #     self.browser.execute_script('window.scrollTo(0, {})'.format(i))
            #     time.sleep(0.2)
            # ele = self.browser.find_element_by_xpath('//li[@data-anchor="#detail"][2]')
            # self.browser.execute_script("arguments[0].scrollIntoView();", ele)
            title = self.browser.find_element_by_xpath('//div[@class="sku-name"]').text.strip()
            # if not hasattr(self,'error_retry'):
            #     if self.key_words[0] not in title:
            #         logging.error('商品不属于此分类 标题:%s 分类:%s'%(title,self.key_words[0]))
            #         return
            if '该商品已下柜' in self.browser.page_source:
                logging.error('该商品已下柜 {}'.format(response.url))
                return
            try:
                promotion_price = self.browser.find_element_by_xpath(
                    '//span[@class="p-price"]/span[2]').text.strip()
            except:
                promotion_price = ''
            if "预约抢购" in self.browser.page_source:
                return
            if promotion_price == '':
                if "预售" in self.browser.page_source:
                    logging.error('预售 {}'.format(response.url))
                    return
                time.sleep(60)
                # 删除 cookie, localStorage, 让浏览器自动获取新cookie 旧cookie 限制爬取需要登录
                # js = 'window.localStorage.clear();'
                # self.browser.execute_script(js)
                # self.browser.delete_all_cookies()
                self.browser.refresh()
                promotion_price = self.browser.find_element_by_xpath(
                    '//span[@class="p-price"]/span[2]').text.strip()
            item['title'] = title
            item['sku_ids'] = ','.join(
                response.xpath('//div[contains(@id,"choose-attr")]//div[@data-sku]/@data-sku').extract())
            try:
                original_text = self.browser.find_element_by_xpath(
                    '//del[@id="page_origin_price" or @id="page_opprice" or @id="page_hx_price"]').text.strip().replace(
                    '￥', '')
            except:
                original_text = ''
            if original_text:
                item['original_price'] = original_text
            if not 'original_price' in item:
                item['original_price'] = promotion_price
                item['promotion_price'] = ''
            else:
                item['promotion_price'] = promotion_price
            if item['promotion_price'] == '' and item['original_price'] == '':
                logging.error("反爬价格无法获取失败")
                self.fail_url_save(response)
                return
            try:
                comment_text = self.browser.find_element_by_xpath(
                    '//a[contains(@class,"count J-comm")]').text.strip()
            except:
                comment_text = self.browser.find_element_by_xpath('//li[@data-anchor="#comment"]/s').text.strip()
                comment_text = comment_text.replace('(', '').replace(')', '')
            if comment_text:
                index = comment_text.find('万')
                if index != -1:
                    item['comment_count'] = int(float(comment_text[:index]) * 10000)
                else:
                    comment_count = re.search('\d+', comment_text)
                    if comment_count:
                        item['comment_count'] = int(comment_count.group())

            if item['comment_count'] == 0:
                self.comment_no_count += 1
            else:
                self.comment_no_count = 0
            item['category'] = self.get_category()
            shop_id = re.findall('shopId.*?(\d+)', self.browser.page_source)[0]
            item['shop_id'] = shop_id
            shop_name = ''
            try:
                shop_name = self.browser.find_element_by_xpath(
                    '//div[@class="J-hove-wrap EDropdown fr"]//div[@class="name"]/a')
            except:
                try:
                    shop_name = self.browser.find_element_by_xpath('//div[@id="popbox"]//h3/a')
                except:
                    pass
            if shop_name:
                shop_name = shop_name.get_attribute('innerText').strip()
                item['shop_name'] = shop_name
            service_ele = self.browser.find_elements_by_xpath(
                '//div[@id="J_SelfAssuredPurchase"]/div[@class="dd"]//a')
            service = []
            for i in service_ele:
                service.append(i.text)
            item['service'] = ','.join(service)
            reputation_keys = self.browser.find_elements_by_xpath('//span[@class="score-desc"]')
            reputation_values = self.browser.find_elements_by_xpath('//span[contains(@class,"score-detail")]/em')
            reputation_list = []
            for j, i in enumerate(reputation_keys):
                reputation_list.append(i.text + ": " + reputation_values[j].text)
            item['url'] = response.url.replace('http:', 'https:')
            item['reputation'] = ' '.join(reputation_list)
            # self.browser.find_element_by_xpath('//li[@data-anchor="#detail"][2]').click()
            detail_keys = self.browser.find_elements_by_xpath('//dl[@class="clearfix"]/dt[not(@class)]')
            detail_values = self.browser.find_elements_by_xpath('//dl[@class="clearfix"]/dd[not(@class)]')
            if len(detail_values) != len(detail_values):
                logging.error('产品参数爬取错误 ' + self.browser.current_url)
                self.fail_url_save(response)
            detail_dict = {}
            detail_str_list = []
            for j, i in enumerate(detail_keys):
                detail_str_list.append(
                    i.get_attribute('innerText') + ':' + detail_values[j].get_attribute('innerText'))
                detail_dict[i.get_attribute('innerText')] = detail_values[j].get_attribute('innerText')
            try:
                brand = self.browser.find_element_by_xpath('//ul[@id="parameter-brand"]//a').get_attribute('innerText')
                if brand:
                    detail_dict['品牌'] = brand
            except:
                pass
            detail_list = self.browser.find_elements_by_xpath('//ul[contains(@class,"parameter2")]/li')
            for j, i in enumerate(detail_list):
                s = i.get_attribute('innerText').replace(' ', '').replace('\n', '').replace('\r', '').replace(
                    '\t', '').replace(
                    '\xa0',
                    '')
                if s.endswith('：') or s.endswith(':'):
                    detail_str_list.append(s + detail_list[j + 1])
                    continue
                if ':' in s or '：' in s:
                    detail_str_list.append(s)
            for i in detail_str_list:
                tmp = re.split('[:：]', i)
                if tmp[0] not in detail_dict:
                    detail_dict[tmp[0]] = tmp[1].replace('\xa0', '')
            item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
            # item['price_range'] = self.get_price_range()
            itemId = re.findall('\d+', response.url)[0]
            item['out_number'] = itemId
            item['site_from'] = 11
            item['site_type'] = 1
            img_urls = []
            img_ele = self.browser.find_elements_by_xpath('//div[@id="spec-list"]/ul/li/img')
            for i in img_ele:
                img_urls.append('http://img10.360buyimg.com/n12/%s' % i.get_attribute('data-url'))
            item['cover_url'] = img_urls[0]
            item['img_urls'] = ','.join(img_urls)
            good_data = dict(item)
            # data = self.get_impression(itemId)
            # good_data.update(data)
            print("原价%s,优惠价%s, 评论%s, 分类%s, 站外编号%s " % (good_data['original_price'], good_data['promotion_price'],
                                                              good_data['comment_count'],
                                                              good_data['category'],
                                                              good_data['out_number']))
            try:
                res = self.s.post(url=self.goods_url, data=good_data)
            except:
                time.sleep(10)
                res = self.s.post(url=self.goods_url, data=good_data)
            if res.status_code != 200 or json.loads(res.content)['code']:
                logging.error("产品保存失败" + response.url)
                logging.error(json.loads(res.content)['message'])
                self.fail_url_save(response)
            else:
                self.suc_count += 1
        except Exception as e:
            logging.error("行号 {}, 产品爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e)))
            self.fail_url_save(response)

    def parse_detail(self, response):
        if self.comment_no_count >= 10:
            # 反爬限制  需要登陆
            self.jd_login()
        if 'passport.jd.com/new/login.aspx' in self.browser.current_url:
            self.browser.get('https://jd.com')
            time.sleep(2)
            if '你好，请登录' in self.browser.page_source:
                self.jd_login()
            else:
                while True:
                    time.sleep(5)
                    try:
                        self.browser.get(response.url)
                        if 'passport.jd.com/new/login.aspx' not in  self.browser.current_url:
                            break
                    except:
                        pass
        if 'pcitem.jd.hk' in self.browser.current_url:  # 京东国际不爬
            logging.error('京东国际 {}'.format(response.url))
        elif 'paimai.jd.com' in self.browser.current_url:  # 京东拍卖不爬
            logging.error('京东拍卖 {}'.format(response.url))
        elif self.browser.current_url == 'https://www.jd.com/?d':
            logging.error('链接异常 {}'.format(response.url))
        else:
            self.detail_data(response)
        self.list_url.pop(0)
        if self.list_url:
            yield scrapy.Request(self.list_url[0], meta={'usedSelenium': True},
                                 callback=self.parse_detail,
                                 dont_filter=True)
        else:
            print(self.fail_url)
            if self.error_retry:
                if self.fail_url:
                    data = self.fail_url.pop(0)
                    self.list_url = data['value']
                    self.category = data['name']
                    # self.price_range = data['price_range']
            else:
                # if self.category in self.price_range_list:
                #     page = self.max_price_page
                # else:
                #     page = self.max_page
                page = self.max_page
                if self.page < page:
                    self.page += 1
                else:
                    self.page = 1
                    # if self.category in self.price_range_list and len(self.price_range_list[self.category]) > 1:
                    #     self.price_range_list[self.category].pop(0)
                    # else:
                    #     self.key_words.pop(0)
                    self.key_words.pop(0)
                if self.key_words:
                    self.category = self.key_words[0]['name']
                    self.max_page = self.key_words[0]['max_page']
                    self.list_url = self.get_list_urls()
            if self.list_url:
                yield scrapy.Request(self.list_url[0], callback=self.parse_detail,
                                     meta={'usedSelenium': True}, dont_filter=True)

    def get_impression(self, itemId):
        data = {}
        cookies = self.browser.get_cookies()
        cookies = [i['name'] + "=" + i['value'] for i in cookies]
        cookies = '; '.join(cookies)

        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.jd.com/%s.html' % itemId,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'cookie': cookies
        }
        url = self.comment_data_url % (itemId, 0)
        try:
            comment_res = self.s.get(url, headers=headers, verify=False, timeout=10)
        except:
            time.sleep(10)
            comment_res = self.s.get(url, headers=headers, verify=False, timeout=10)
        rex = re.compile('({.*})')
        result = json.loads(rex.findall(comment_res.text)[0])
        data['positive_review'] = result['productCommentSummary']['goodCount']
        data['comment_count'] = result['productCommentSummary']['commentCount']
        impression = ''
        for j in result['hotCommentTagStatistics']:
            impression += j['name'] + '(' + str(j['count']) + ')  '
        data['impression'] = impression
        return data

    # def get_price_range(self):
    #     price_range = ''
    #     if self.error_retry:
    #         price_range = self.price_range
    #     else:
    #         if self.key_words and self.key_words[0]['name'] in self.price_range_list:
    #             price_range = self.price_range_list[self.key_words[0]['name']][0]
    #             temp = re.findall('(\d+)', price_range)
    #             price_range = temp[0] + "-" + temp[1] if len(temp) > 1 else temp[0] + '以上'
    #     return price_range

    def get_category(self):
        if self.category == '真无线蓝牙耳机 降噪 入耳式':
            return '耳机'
        else:
            return self.category

    def jd_login(self):
        if '你好，请登录' in self.browser.page_source or '欢迎登录' in self.browser.page_source:
            account_information = random.choice(self.jd_account_list)
            if not account_information:
                logging.error('暂无账号信息，反爬限制')
                return
            res = self.s.get('http://127.0.0.1:%s/json/version' % self.se_port)
            browser_ws_endpoint = json.loads(res.content)['webSocketDebuggerUrl']
            asyncio.get_event_loop().run_until_complete(
                jd_code(account_information['account'], account_information['password'], browser_ws_endpoint))
            self.comment_no_count = 0
