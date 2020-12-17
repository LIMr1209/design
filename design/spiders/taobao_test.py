import json
import os
import re
import time
from urllib import parse

import requests
import scrapy
from pymongo import MongoClient
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import logging

from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider


class TaobaoSpider(SeleniumSpider):
    name = "taobao_test"
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }
    goods_url = 'https://opalus.d3ingo.com/api/goods/save'

    def __init__(self, key_words, *args, **kwargs):
        self.fail_url = []
        self.suc_count = 0
        self.key_words = "真无线蓝牙耳机 降噪 入耳式"
        # self.cookie = 'cookie2=1e1329c204b483965c50f4aea175989c; t=27342fccaf0252611c51fc03fa4e7ac6; _tb_token_=f353e3600a381; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; _samesite_flag_=true; xlly_s=1; enc=MIfEinE%2BUqe%2FrOAJ4kSL2sf8sPaGqMfQhs3fJI6jVi9whtay9lqef7PafAH8YbF%2Bpb%2FPiEz6i%2FJP%2B7yEO0dpYA%3D%3D; lLtC1_=1; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az9h5Tq7%2Bg%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; _m_h5_tk=6ccde694cfdbc1922b28debd3c328878_1606968670174; _m_h5_tk_enc=a5534a7aa9920b87606b4df020bf73f7; tfstk=cCxAB_2ebbcDOl6JLE3u5zLb7qLAZrqA6-1UXvR2soXxpsrOi4-Hvhbil9FA2YC..; l=eBjqXoucQKR1CZ0kBOfZourza77tIIRYouPzaNbMiOCPOqC950zhWZROM0LpCnGVhssJR3oVpXawBeYBqn4xIghne5DDwIMmn; isg=BJKSTHvrGeWwvmT7yvjYunE041h0o5Y9lxlgOFzrtsUwbzJpRDEeTWCN28vTGQ7V'
        self.cookie = 'hng=CN%7Czh-CN%7CCNY%7C156; t=27342fccaf0252611c51fc03fa4e7ac6; enc=MIfEinE%2BUqe%2FrOAJ4kSL2sf8sPaGqMfQhs3fJI6jVi9whtay9lqef7PafAH8YbF%2Bpb%2FPiEz6i%2FJP%2B7yEO0dpYA%3D%3D; _tb_token_=f353e3600a381; cookie2=1e1329c204b483965c50f4aea175989c; xlly_s=1; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; cna=zasMF12t3zoCATzCuQKpN3kO; uc1=existShop=false&cookie21=UtASsssmeW6lpyd%2BB%2B3t&cookie14=Uoe0az9h5Ti4KA%3D%3D&pas=0&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D; uc3=lg2=UIHiLt3xD8xYTw%3D%3D&vt3=F8dCuf2CSp7DjbEF1as%3D&id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSdvtCI6XCk%2F&nk4=0%400AdtZS03tnds0llDWCRcSihqN1jxbD1O2opb; sgcookie=E100PSo4OpJklR8obNtKBryUufO195A5YSzyXhka2trDZeXqTdHNTDWmqifymuuq1627cAyn3cQnqskk9ztKGfP43g%3D%3D; csg=2a17af03; pnm_cku822=098%23E1hv%2F9vUvbpvUvCkvvvvvjiWP2dyQjnmn2dwgj1VPmPO6jr8RFswzj3WPFSv0jYURvhvCvvvvvvUvpCWCRbXvvaF9W2%2BFfmtEpcZTWexRdIAcUmxfwofd56Ofa3lKbh6UxWnSXVxI2iI27zh1j7ZHkx%2F1RBlYb8rwZXlJXxreC9aWXxr1WmK5I9CvvOUvvVvJhTIvpvUvvmvR0nopE4gvpvIvvvvvhCvvvvvvUUvphvUbpvv99Cvpv32vvmmvhCvmWIvvUUvphvUA9vCvvOvCvvvphvRvpvhvv2MMTOCvvpvvUmm; _m_h5_tk=b89879a97398b54808462f75f2281c05_1606972762508; _m_h5_tk_enc=27f9ec8ed65873154cb5f358e7cc2baf; tfstk=cplGB7MRRAy_J-2nFCNsruEv8P-dZrtabjltTXaIUF2atkGFigBFUcbp-koiMt1..; l=eBQJ2fCIQDOlzshQBOfZlurza77OhIRYouPzaNbMiOCPOT5e5omlWZROa_TwCnGVh6cBR3oVpXaaBeYBqhvQ5O95a6Fy_pHmn; isg=BPv7i6eNIMq3nB1mTJyyKlytit9lUA9SVto5X-24ufoRTBsudSELooqGZuwC6mdK; cq=ccp%3D1'
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.browser.get('https://www.taobao.com/')
        # self.browser.get('https://www.tmall.com/')

    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        cookies = []
        cookie = self.cookie
        items = cookie.split(';')
        for item in items:
            itemDict = {}
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict['name'] = key
            itemDict['value'] = value
            itemDict['path'] = '/'
            itemDict['domain'] = '.taobao.com'
            # itemDict['domain'] = '.tmall.com'
            itemDict['expires'] = None
            cookies.append(itemDict)
        for i in cookies:
            self.browser.add_cookie(i)

    # 更换登陆信息
    def update_cookie(self):
        self.browser.delete_all_cookies()  # 删除cookie
        login_url = 'https://login.taobao.com/member/login.jhtml'
        username = '斌爷爷1058169464'
        password = 'aaa1058169464'
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
        # self.stringToDict()
        list_url = ['https://item.taobao.com/item.htm?id=631111207972',
 'https://item.taobao.com/item.htm?id=631112835907']
        if list_url:
            yield scrapy.Request(list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True, 'list_url': list_url})

    def parse_detail(self, response):
        if "detail.tmall.com" in response.url:
            self.save_tmall_data(response)
        if "item.taobao.com" in response.url:
            self.save_taobao_data(response)
        list_url = response.meta['list_url']
        list_url.pop(0)
        # time.sleep(1)
        if list_url:
            yield scrapy.Request(list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True, "list_url": list_url})

    def save_tmall_data(self, response):
        time.sleep(2)
        choice = "1"
        try:
            code_ele = self.browser.find_element_by_id('sufei-dialog-content')
            if code_ele:
                # choice = input('请输入您的选择：')
                close_ele = self.browser.find_element_by_id('sufei-dialog- close')
                if close_ele:
                    close_ele.click()
        except:
            pass
        finally:
            if choice == '1':
                try:
                    height = 0
                    for i in range(height, 1500, 200):
                        self.browser.execute_script('window.scrollTo(0, {})'.format(i))
                        time.sleep(0.5)
                    # ele = self.browser.find_element_by_xpath('//div[@class="tm-layout"]')
                    # self.browser.execute_script("arguments[0].scrollIntoView();", ele)
                    elem = WebDriverWait(self.browser, 10, 0.5).until(
                        EC.presence_of_element_located(
                            (By.ID, 'side-shop-info')
                        )
                    )
                    if elem:
                        item = TaobaoItem()
                        item['title'] = self.browser.find_element_by_xpath(
                            '//div[@class="tb-detail-hd"]/h1').text.strip()
                        try:
                            item['original_price'] = self.browser.find_element_by_xpath(
                                '//dl[@id="J_StrPriceModBox"]//span').text
                        except:
                            item['original_price'] = self.browser.find_element_by_xpath(
                                '//span[@class="tm-price"]').text
                        try:
                            item['promotion_price'] = self.browser.find_element_by_xpath(
                                '//dl[@id="J_PromoPrice"]//span').text
                        except:
                            item['promotion_price'] = ''

                        service = self.browser.find_elements_by_xpath('//ul[@class="tb-serPromise"]/li/a')
                        item['service'] = ','.join([i.text for i in service])
                        reputation = self.browser.find_elements_by_xpath('//span[@class="shopdsr-score-con"]')
                        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                            reputation[0].text.strip(), reputation[1].text.strip(), reputation[2].text.strip())
                        try:
                            item['comment_count'] = self.browser.find_element_by_xpath(
                                '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').text
                        except:
                            pass
                        try:
                            sale_xpath = self.browser.find_element_by_xpath(
                                '//*[@id="J_DetailMeta"]//li[@class="tm-ind-item tm-ind-sellCount"]//span[@class="tm-count"]').text
                            if sale_xpath:
                                index = sale_xpath.find('万')
                                if index != -1:
                                    item['sale_count'] = int(float(sale_xpath[:index]) * 10000)
                                else:
                                    sale_count = re.search('\d+', sale_xpath)
                                    if sale_count:
                                        item['sale_count'] = int(sale_count.group())
                        except:
                            pass
                        try:
                            elem = WebDriverWait(self.browser, 20, 0.5).until(
                                EC.presence_of_element_located(
                                    (By.ID, 'J_CollectCount')
                                )
                            )
                            if elem.is_displayed:
                                favorite_count_text = self.browser.find_element_by_xpath('//span[@id="J_CollectCount"]')
                                d = re.search("\d+", favorite_count_text.text)
                                if d:
                                    item['favorite_count'] = int(d.group())
                        except:
                            item['favorite_count'] = 0
                        detail_list = response.xpath('//ul[@id="J_AttrUL"]/li/text()').extract()
                        detail_str_list = []
                        for j, i in enumerate(detail_list):
                            s = i.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0',
                                                                                                                 '')
                            if s.endswith('：') or s.endswith(':'):
                                detail_str_list.append(s + detail_list[j + 1])
                                continue
                            if ':' in s or '：' in s:
                                detail_str_list.append(s)
                        item['detail_str'] = ', '.join(detail_str_list)
                        detail_dict_list = []
                        for i in detail_str_list:
                            tmp = re.split('[:：]', i)
                            temp = {tmp[0]: tmp[1].replace('\xa0', '')}
                            detail_dict_list.append(temp)
                        item['detail_dict'] = json.dumps(detail_dict_list, ensure_ascii=False)

                        try:
                            cover_url = self.browser.find_element_by_xpath(
                                '//ul[@id="J_UlThumb"]/li//img').get_attribute(
                                'src')
                            if not cover_url.startswith("http"):
                                cover_url = "https:" + cover_url
                            cover_url = cover_url.rsplit('_', 1)[0]
                        except:
                            cover_url = ''
                        item['cover_url'] = cover_url
                        itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]

                        item['site_from'] = 9
                        item['site_type'] = 1
                        item['out_number'] = itemId
                        item['category'] = self.key_words
                        item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
                        good_data = dict(item)
                        # if 'sale_count' in good_data:
                        #     good_data.pop('sale_count')
                        # good_data.pop('service')
                        # good_data.pop('cover_url')
                        # good_data.pop('promotion_price')
                        # good_data.pop('original_price')
                        res = requests.post(url=self.goods_url, data=good_data)
                        if res.status_code != 200 or json.loads(res.content)['code']:
                            logging.error("产品保存失败" + response.url)
                            logging.error(json.loads(res.content)['message'])
                            self.fail_url.append(response.url)

                except Exception as e:
                    logging.error(
                        "文件 {}".format(e.__traceback__.tb_frame.f_globals["__file__"])
                    )  # 文件
                    logging.error("行号 {}".format(e.__traceback__.tb_lineno))  # 行号
                    logging.error("产品爬取失败 {} {}".format(response.url, str(e)))

    def save_taobao_data(self, response):
        # time.sleep(2)
        choice = "1"
        try:
            code_ele = self.browser.find_element_by_id('sufei-dialog-content')
            if code_ele:
                # choice = input('请输入您的选择：')
                close_ele = self.browser.find_element_by_id('sufei-dialog- close')
                if close_ele:
                    close_ele.click()
        except:
            pass
        finally:
            if choice == '1':
                try:
                    ele = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]')
                    self.browser.execute_script("arguments[0].scrollIntoView();", ele)
                    item = TaobaoItem()
                    item['title'] = self.browser.find_element_by_xpath('//h3[@class="tb-main-title"]').text.strip()
                    item['original_price'] = self.browser.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').text.strip()
                    try:
                        item['promotion_price'] = self.browser.find_element_by_xpath(
                            '//*[@id="J_PromoPriceNum"]').text.strip()
                    except:
                        item['promotion_price'] = ''
                    service = self.browser.find_elements_by_xpath('//dt[contains(text(),"承诺")]/following-sibling::dd/a')
                    item['service'] = ','.join([i.text for i in service])
                    try:
                        reputation = self.browser.find_elements_by_xpath('//dd[contains(@class,"tb-rate-")]/a')
                        if not reputation:
                            reputation = self.browser.find_elements_by_xpath(
                                '//li[@class="shop-service-info-item"]//em')
                        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                            reputation[0].text.strip(), reputation[1].text.strip(), reputation[2].text.strip())
                    except:
                        item['reputation'] = ''
                    try:
                        if not item['reputation']:
                            reputation = self.browser.find_elements_by_xpath(
                                '//li[@class="shop-service-info-item"]//em')
                            item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                                reputation[0].text.strip(), reputation[1].text.strip(), reputation[2].text.strip())
                    except:
                        pass
                    try:
                        item['comment_count'] = self.browser.find_element_by_xpath(
                            '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').text
                    except:
                        pass
                    sale_xpath = self.browser.find_element_by_xpath('//*[@id="J_SellCounter"]').text
                    if sale_xpath:
                        index = sale_xpath.find('万')
                        if index != -1:
                            item['sale_count'] = int(float(sale_xpath[:index]) * 10000)
                        else:
                            if sale_xpath == '-':
                                print("产品爬取失败", response.url, str("验证码"))
                                self.fail_url.append(response.url)
                            sale_count = re.search('\d+', sale_xpath)
                            if sale_count:
                                item['sale_count'] = int(sale_count.group())
                    try:
                        elem = WebDriverWait(self.browser, 20, 0.5).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'J_FavCount')
                            )
                        )
                        if elem.is_displayed:
                            favorite_count_text = self.browser.find_element_by_xpath('//em[@class="J_FavCount"]')
                            d = re.search("\d+", favorite_count_text.text)
                            if d:
                                item['favorite_count'] = int(d.group())
                    except:
                        item['favorite_count'] = 0
                    itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]
                    detail_list = response.xpath('//ul[@class="attributes-list"]/li//text()').extract()
                    detail_str_list = []
                    for j, i in enumerate(detail_list):
                        s = i.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '')
                        if s:
                            if s.endswith('：') or s.endswith(':'):
                                detail_str_list.append(s + detail_list[j + 1])
                                continue
                            if ':' in s or '：' in s:
                                detail_str_list.append(s)
                    item['detail_str'] = ', '.join(detail_str_list)
                    detail_dict_list = []
                    for i in detail_str_list:
                        tmp = re.split('[:：]', i)
                        temp = {tmp[0]: tmp[1].replace('\xa0', '')}
                        detail_dict_list.append(temp)
                    item['detail_dict'] = json.dumps(detail_dict_list, ensure_ascii=False)
                    try:
                        cover_url = self.browser.find_element_by_xpath('//ul[@id="J_UlThumb"]/li//img').get_attribute(
                            'src')
                        if not cover_url.startswith("http"):
                            cover_url = "https:" + cover_url

                        cover_url = cover_url.rsplit('_', 1)[0]
                    except Exception as e:
                        cover_url = ''
                    item['cover_url'] = cover_url
                    item['site_from'] = 8
                    item['site_type'] = 1
                    item['out_number'] = itemId
                    item['category'] = self.key_words
                    item['url'] = 'https://item.taobao.com/item.htm?id=' + str(itemId)
                    good_data = dict(item)
                    if 'sale_count' in good_data:
                        good_data.pop('sale_count')
                    good_data.pop('service')
                    good_data.pop('cover_url')
                    good_data.pop('promotion_price')
                    good_data.pop('original_price')
                    res = requests.post(url=self.goods_url, data=good_data)
                    if res.status_code != 200 or json.loads(res.content)['code']:
                        logging.error("产品保存失败" + response.url)
                        logging.error(json.loads(res.content)['message'])
                        self.fail_url.append(response.url)

                except Exception as e:
                    logging.error(
                        "文件 {}".format(e.__traceback__.tb_frame.f_globals["__file__"])
                    )  # 文件
                    logging.error("行号 {}".format(e.__traceback__.tb_lineno))  # 行号
                    logging.error("产品爬取失败 {} {}".format(response.url, str(e)))
                    self.fail_url.append(response.url)
