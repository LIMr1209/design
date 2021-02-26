import json
import os
import re
import time
from urllib import parse

import requests
import scrapy
from fake_useragent import UserAgent
from pydispatch import dispatcher
from requests.adapters import HTTPAdapter
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import logging

from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider


# 解析源代码方式获取sku 价格
def sku_price_func(browser, site_from):
    page_source = browser.page_source
    rex = re.compile('skuMap.*(\{";.*?}})')
    try:
        res = re.findall(rex, page_source)[0]
    except:
        return ''
    sku_price = json.loads(res)
    detail_price = []
    for i, j in sku_price.items():
        original_price = j['price']
        skuid = j['skuId']
        style = {}
        style_list_num = i.split(';')
        for z in style_list_num:
            if z:
                try:
                    ele = browser.find_element_by_xpath('//li[@data-value="{}"]'.format(z))
                except:
                    continue
                cate = ele.find_element_by_xpath('../../ul').get_attribute('data-property')
                text = ele.find_element_by_xpath('./a/span').get_attribute('innerText')
                style[cate] = text
        detail_price.append({
            'skuid': skuid,
            'original_price': original_price,
            'style': style
        })
    return detail_price


# 自动化方式获取sku 价格
def dynloop_rcsn(browser, site_from):
    data = []
    cate_list = []
    sku_name_list = browser.find_elements_by_xpath('//ul[contains(@class,"J_TSaleProp")]')
    for i in sku_name_list:
        data.append(i.find_elements_by_xpath('./li'))
        cate_list.append(i.get_attribute('data-property'))

    def dynloop_inner_rcsn(browser, data, cate_list, site_from, cur_y_idx=0, detail_price=[]):
        max_y_idx = len(data) - 1
        for x_idx in range(len(data[cur_y_idx])):
            ActionChains(browser).move_to_element(data[cur_y_idx][x_idx]).perform()
            # browser.execute_script('window.scrollTo(0, 20)')
            if not data[cur_y_idx][x_idx].get_attribute('class'):
                data[cur_y_idx][x_idx].find_element_by_xpath('./a').click()
            if cur_y_idx == max_y_idx:
                if site_from == 9:
                    try:
                        original_price = browser.find_element_by_xpath(
                            '//dl[@id="J_StrPriceModBox"]//span').get_attribute('innerText')
                    except:
                        original_price = browser.find_element_by_xpath(
                            '//span[@class="tm-price"]').get_attribute('innerText')
                    try:
                        promotion_price = browser.find_element_by_xpath(
                            '//dl[@id="J_PromoPrice"]//span').get_attribute('innerText')
                    except:
                        promotion_price = ''
                else:
                    original_price = browser.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').get_attribute('innerText').strip()
                    try:
                        promotion_price = browser.find_element_by_xpath(
                            '//*[@id="J_PromoPriceNum"]').get_attribute('innerText').strip()
                    except:
                        promotion_price = ''
                style_list = browser.find_elements_by_xpath('//li[@class="tb-selected"]/a/span')
                name = ''
                for i in range(len(style_list)):
                    # display none 的标签 无法 text 拿到文本 通过属性拿取
                    name += cate_list[i] + ':' + style_list[i].get_attribute('innerText') + '\n'
                detail_price.append({
                    'name': name,
                    'original_price': original_price,
                    'promotion_price': promotion_price
                })
            else:
                dynloop_inner_rcsn(browser, data, cate_list, site_from, cur_y_idx + 1, detail_price)
        return detail_price

    return dynloop_inner_rcsn(browser, data, cate_list, site_from)


def get_track(distance):  # distance为传入的总距离
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.1
    # 初速度
    v = 0

    while current < distance:
        if current < mid:
            # 加速度为2
            a = 50
        else:
            # 加速度为-2
            a = -10
        v0 = v
        # 当前速度
        v = v0 + a * t
        # 移动距离
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track


class TaobaoSpider(SeleniumSpider):
    name = "taobao_new"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, *args, **kwargs):
        self.page = 1
        self.max_page = kwargs['max_page']
        # self.max_price_page = 7  # 价格区间的爬10页
        self.price_range_list = {
            '吹风机': ['[459,750]', '[751,999]', '[1000,]'],
            '真无线蓝牙耳机 降噪 入耳式': ['[300, 900]', '[900,3000]'],
        }
        self.key_words = kwargs['key_words'].split(',')
        self.fail_url = {}
        self.suc_count = 0
        self.error_retry = 0
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.goods_url = self.setting['OPALUS_GOODS_URL']
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.search_url = 'https://s.taobao.com/search?q={name}&filter=reserve_price{price_range}&s={page_count}&tab=all'

        super(TaobaoSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.taobao.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error(self.key_words)
        logging.error(self.page)
        logging.error(self.price_range_list)
        logging.error(self.fail_url)

    # 滑块破解
    def selenium_code(self):
        time.sleep(2)
        try:
            # self.browser.find_element_by_id("sufei-dialog-content")
            self.browser.switch_to.frame('sufei-dialog-content')
            try:
                self.browser.find_element_by_xpath('//div[@class="warnning-text"]')
                return {'success': False}
            except:
                self.browser.switch_to.default_content()
                return {'success': True}
            # noinspection PyUnreachableCode
            button = self.browser.find_element_by_xpath('//span[@class="nc_iconfont btn_slide"]')
            action = ActionChains(self.browser)
            action.click_and_hold(button).perform()
            tracks = get_track(300)
            for x in tracks:
                action.move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(2)
            self.browser.switch_to.default_content()
            self.selenium_code()
        except:
            return {'success': True}

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
        # cookies = self.browser.get_cookies()
        # fw = open('tmp/taobao.cookie', 'w')
        # fw.write(json.dumps(cookies))
        # fw.close()
        # self.update_cookie()
        # self.stringToDict()
        # list_url = self.get_list_urls()
        # 爬取失败重新爬取
        list_url = ['https://detail.tmall.com/item.htm?id=601311035860&ad_id=&am_id=&cm_id=140105335569ed55e27b&pm_id=&abbucket=16', 'https://detail.tmall.com/item.htm?id=617605724471&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610868778920&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=556573057890&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613152558653&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=537891514461&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=612149637277&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614131606425&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=566140365862&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=560955327415&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=568581864005&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=602521336485&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=581281473870&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615767572861&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=572792522701&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615529504288&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=632594246459&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625156739619&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628506179836&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615898383771&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=530589662007&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=41464129793&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=40609737633&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=623901405199&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626310033267&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609488048875&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610092459479&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=591745548919&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609506220126&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628626084553&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604784330225&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627608696566&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615090035649&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=600197182491&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633072687255&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633712429364&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631498911592&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=601311035860&ad_id=&am_id=&cm_id=140105335569ed55e27b&pm_id=&abbucket=16', 'https://detail.tmall.com/item.htm?id=617605724471&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610868778920&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=634637965486&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615022126247&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=597886110526&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626544806622&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635584305852&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609740875462&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=551913075897&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=611916248803&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=595225614263&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625612817040&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=600554010392&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=620466618820&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=592376521275&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627030998826&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625311258782&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624658847797&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626382473060&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=523187052620&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=577693020638&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635636913246&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=580102611439&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=606432215075&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=536417910358&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=578049978983&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627774350818&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=593538805729&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=598236456479&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614694880651&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635991220022&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=634406837471&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610675213710&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=638760327079&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=634309868085&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=531110930450&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=605637409461&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624962729394&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604301354715&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615265994111&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=571698250046&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=605744040891&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=534045642021&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=600395782841&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=569578995446&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=558045831457&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=629556204931&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=570223781410&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625629547615&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631945412821&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=597635589956&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626175486410&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=599623043090&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633612806942&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=619813706831&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=634308504310&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=578621524999&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=620018515194&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631024259493&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=602184349580&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624509973684&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=594646610252&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=593707615207&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=619368531030&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615087033888&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=596531256683&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626657394666&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624440894797&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628460479000&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=623399314137&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627342494757&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=592298871609&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=17539777212&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=575359517214&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626521274822&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=630430629393&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609755141615&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=526964453473&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604472574344&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=632201029113&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=603064746701&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=629228281044&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=601819569246&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613513558918&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=592976383128&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635459482133&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=528047167188&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=530782670428&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610224119648&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=590048985411&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=605601771361&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=638519575372&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610549818624&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=632374809190&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=583120672290&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=534039820524&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624973743283&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615010893412&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=637478631297&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614130406384&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=527609770144&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610915254018&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=616316943154&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626611693792&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=585106692831&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610154009288&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=43819977668&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=524817229189&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=44712532485&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633866611855&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628261203704&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=522687638331&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=593098537137&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=574010198393&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=578233006298&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=528701553145&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=617206045393&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613947830448&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=598584821644&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624226942011&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633699514822&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604215709129&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625433385698&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=574406619267&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610396386213&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=561129246416&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=579578109658&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626463049369&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627362749832&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628681971663&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613700577502&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=630780786410&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=630104117117&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=588552510253&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631921716868&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626700225433&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=605095757127&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=630604852563&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633507301777&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609609530897&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=633951681478&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604848924630&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=611976449249&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604008488610&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=556043196484&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=556043196484&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=533226307878&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=611316149350&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613449345072&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=578761681286&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=589109050458&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=589849167503&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627913479634&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=591364010480&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=621054426593&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609108813831&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626066555557&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=526935961434&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627655754190&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=596398309694&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=626465575178&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=568868219109&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=567161471358&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614515131166&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=618342736891&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628745493555&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=528635265670&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614154394738&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=624939480743&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=566046999723&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=621897185381&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=540275929536&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=623650485691&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=620719838353&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=560841665537&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=585874031151&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=527731460944&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=562076322426&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615021113306&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628501122961&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625764611923&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=556779942509&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=39456494055&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=522198496171&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635841999503&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=541018466265&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=636676637722&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=540509925595&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=587066046235&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=564513302461&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=617209385615&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628306556799&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=563619142537&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=583073174302&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=630615338604&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=625328147770&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=600454319902&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=42254642319&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=607584713377&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=554828708538&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=574406915343&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=578994373748&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=568258029089&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=619279062620&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=614695640424&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615928647526&ns=1&abbucket=16']
        self.category = '电热水器'
        self.error_retry = 1
        yield scrapy.Request(list_url[0], callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True, 'list_url': list_url})

    def get_list_urls(self):
        self.browser.get('https://www.taobao.com/')
        self.browser.find_element_by_id('q').send_keys(self.key_words[0])
        self.browser.find_element_by_xpath('//div[@class="search-button"]/button').click()
        time.sleep(2)
        self.page += 1
        max_page = self.browser.find_element_by_xpath('//div[@class="total"]').get_attribute('innerText')
        self.max_page = int(re.search('\d+', max_page).group())
        if self.max_page >= 15:
            self.max_page = 15
        list_urls = []
        list_url = self.browser.find_elements_by_xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a')
        for i in list_url:
            list_urls.append(i.get_attribute('href'))
        while self.page <= self.max_page:
            next = self.browser.find_elements_by_xpath('//a[@class="J_Ajax num icon-tag"]')
            if len(next) > 1:
                next[1].click()
            else:
                next[0].click()
            time.sleep(2)
            self.page += 1
            list_url = self.browser.find_elements_by_xpath(
                '//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a')
            for i in list_url:
                list_urls.append(i.get_attribute('href'))
        return list_urls

    def fail_url_save(self, response):
        if self.error_retry:
            if self.category in self.fail_url:
                self.fail_url[self.category].append(response.url)
            else:
                self.fail_url[self.category] = [response.url]
        else:
            if self.key_words[0] in self.fail_url:
                self.fail_url[self.key_words[0]].append(response.url)
            else:
                self.fail_url[self.key_words[0]] = [response.url]

    def parse_detail(self, response):
        time.sleep(4)
        res = {}
        if 'detail.tmall.hk' in self.browser.current_url:
            logging.error("天猫国际" + self.browser.current_url)
        if "detail.tmall.com" in self.browser.current_url:
            res = self.save_tmall_data(response)
        if "item.taobao.com" in self.browser.current_url:
            res = self.save_taobao_data(response)
        # fr = open('tmp/taobao.cookie', 'r')
        # cookies = json.loads(fr.read())
        # fr.close()
        # for i in cookies:
        #     self.browser.add_cookie(i)
        if res:
            if not res['success']:
                self.fail_url_save(response)
                logging.error(res['message'])
            else:
                respon = res['res']
                try:
                    if respon.status_code != 200 or json.loads(respon.content)['code']:
                        logging.error("产品保存失败" + response.url)
                        logging.error(json.loads(respon.content)['message'])
                        self.fail_url_save(response)
                except:
                    self.fail_url_save(response)
                else:
                    self.suc_count += 1
        list_url = response.meta['list_url']
        list_url.pop(0)
        if list_url:
            yield scrapy.Request(list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True, "list_url": list_url}, dont_filter=True, )
        else:
            print(self.fail_url)
            if self.error_retry == 0:
                self.page = 1
                if self.key_words[0] in self.price_range_list and len(self.price_range_list[self.key_words[0]]) > 1:
                    self.price_range_list[self.key_words[0]].pop(0)
                else:
                    self.key_words.pop(0)
                if self.key_words:
                    list_url = self.get_list_urls()
                    yield scrapy.Request(list_url[0], callback=self.parse_detail, dont_filter=True,
                                         meta={'usedSelenium': True, 'list_url': list_url})

    def save_tmall_data(self, response):
        # time.sleep(2)
        choice = "1"
        try:
            pass
            # res = self.selenium_code()
            # 休息会吧
            # if not res['success']:
            #     choice = input('出现验证码 自动验证失败 请手动验证，请输入您的选择：1.通过 2.未通过')
        except:
            pass
        finally:
            if choice == '1':
                try:
                    # try:
                    #     elem = WebDriverWait(self.browser, 10, 0.5).until(
                    #         EC.presence_of_element_located(
                    #             (By.ID, 'side-shop-info')
                    #         )
                    #     )
                    # except:
                    #     pass
                    item = TaobaoItem()
                    try:
                        elem = WebDriverWait(self.browser, 10, 0.5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//span[@class="tm-price"]')
                            )
                        )
                    except:
                        self.browser.refresh()
                        time.sleep(2)
                    try:
                        elem = WebDriverWait(self.browser, 10, 0.5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]')
                            )
                        )
                    except:
                        self.browser.refresh()
                        time.sleep(2)
                    try:
                        item['original_price'] = self.browser.find_element_by_xpath(
                            '//dl[@id="J_StrPriceModBox"]//span').get_attribute('innerText')
                    except:
                        item['original_price'] = self.browser.find_element_by_xpath(
                            '//span[@class="tm-price"]').get_attribute('innerText')
                    try:
                        item['promotion_price'] = self.browser.find_element_by_xpath(
                            '//dl[@id="J_PromoPrice"]//span').get_attribute('innerText')
                    except:
                        item['promotion_price'] = ''
                    detail_price = sku_price_func(self.browser, 9)
                    height = 0
                    for i in range(height, 1500, 200):
                        self.browser.execute_script('window.scrollTo(0, {})'.format(i))
                        time.sleep(0.5)
                    # ele = self.browser.find_element_by_xpath('//div[@class="tm-layout"]')
                    # self.browser.execute_script("arguments[0].scrollIntoView();", ele)

                    item['detail_sku'] = json.dumps(detail_price)
                    item['title'] = self.browser.find_element_by_xpath(
                        '//div[@class="tb-detail-hd"]/h1').get_attribute('innerText').strip()
                    service = self.browser.find_elements_by_xpath('//ul[@class="tb-serPromise"]/li/a')
                    item['service'] = ','.join([i.get_attribute('innerText') for i in service])
                    try:
                        reputation = self.browser.find_elements_by_xpath('//span[@class="shopdsr-score-con"]')
                        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                            reputation[0].get_attribute('innerText').strip(),
                            reputation[1].get_attribute('innerText').strip(),
                            reputation[2].get_attribute('innerText').strip())
                    except:
                        pass
                    try:
                        item['comment_count'] = self.browser.find_element_by_xpath(
                            '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').get_attribute('innerText')
                    except:
                        pass
                    sale_xpath = self.browser.find_element_by_xpath(
                        '//*[@id="J_DetailMeta"]//li[@class="tm-ind-item tm-ind-sellCount"]//span[@class="tm-count"]').get_attribute(
                        'innerText')
                    if sale_xpath:
                        index = sale_xpath.find('万')
                        if index != -1:
                            item['sale_count'] = int(float(sale_xpath[:index]) * 10000)
                        else:
                            sale_count = re.search('\d+', sale_xpath)
                            if sale_count:
                                item['sale_count'] = int(sale_count.group())
                    try:
                        elem = WebDriverWait(self.browser, 20, 0.5).until(
                            EC.presence_of_element_located(
                                (By.ID, 'J_CollectCount')
                            )
                        )
                        if elem.is_displayed:
                            favorite_count_text = self.browser.find_element_by_xpath('//span[@id="J_CollectCount"]')
                            d = re.search("\d+", favorite_count_text.get_attribute('innerText'))
                            if d:
                                item['favorite_count'] = int(d.group())
                    except:
                        item['favorite_count'] = 0
                    detail_keys = self.browser.find_elements_by_xpath(
                        '//table[@class="tm-tableAttr"]/tbody/tr[@class=""]/th')
                    if not detail_keys:
                        detail_keys = self.browser.find_elements_by_xpath(
                            '//table[@class="tm-tableAttr"]/tbody/tr[not(@class)]/th')
                    detail_values = self.browser.find_elements_by_xpath(
                        '//table[@class="tm-tableAttr"]/tbody/tr[@class=""]/td')
                    if not detail_values:
                        detail_values = self.browser.find_elements_by_xpath(
                            '//table[@class="tm-tableAttr"]/tbody/tr[not(@class)]/td')
                    detail_dict = {}
                    detail_str_list = []
                    for j, i in enumerate(detail_keys):
                        detail_str_list.append(
                            i.get_attribute('innerText').replace('\xa0', '').replace('.', '') + ':' + detail_values[
                                j].get_attribute(
                                'innerText').replace('\xa0', ''))
                        detail_dict[i.get_attribute('innerText').replace('\xa0', '').replace('.', '')] = detail_values[
                            j].get_attribute(
                            'innerText').replace('\xa0', '')
                    if not detail_dict:
                        detail_list = self.browser.find_elements_by_xpath('//ul[@id="J_AttrUL"]/li')
                        for j, i in enumerate(detail_list):
                            s = i.get_attribute('innerText').replace(' ', '').replace('\n', '').replace('\r',
                                                                                                        '').replace(
                                '\t', '').replace('\xa0', '').replace('.', '')
                            if s.endswith('：') or s.endswith(':'):
                                detail_str_list.append(s + detail_list[j + 1].get_attribute('innerText'))
                                continue
                            if ':' in s or '：' in s:
                                detail_str_list.append(s)
                        item['detail_str'] = ', '.join(detail_str_list)
                        detail_dict = {}
                        for i in detail_str_list:
                            tmp = re.split('[:：]', i)
                            detail_dict[tmp[0]] = tmp[1].replace('\xa0', '')
                    item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
                    item['detail_str'] = ', '.join(detail_str_list)
                    try:
                        img_urls = []
                        img_urls_ele = self.browser.find_elements_by_xpath(
                            '//ul[@id="J_UlThumb"]/li//img')
                        for i in img_urls_ele:
                            img_url = i.get_attribute('src')
                            if not img_url.startswith("http"):
                                img_url = "https:" + img_url
                            img_url = img_url.rsplit('_', 1)[0]
                            img_urls.append(img_url)
                        item['cover_url'] = img_urls[0]
                        item['img_urls'] = ','.join(img_urls)
                    except:
                        pass
                    itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]

                    item['site_from'] = 9
                    item['site_type'] = 1
                    if self.key_words[0] in self.price_range_list:
                        price_range = self.price_range_list[self.key_words[0]][0]
                        temp = re.findall('(\d+)', price_range)
                        item['price_range'] = temp[0] + "-" + temp[1] if len(temp) > 1 else temp[0] + '以上'
                    else:
                        item['price_range'] = ''
                    item['out_number'] = itemId
                    if self.key_words[0] == '真无线蓝牙耳机 降噪 入耳式':
                        item['category'] = '耳机'
                    else:
                        item['category'] = self.key_words[0]
                    if hasattr(self, 'category'):
                        item['category'] = self.category
                    item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
                    # impression = self.get_impression(itemId)
                    # item['impression'] = impression
                    good_data = dict(item)
                    print(good_data['original_price'], good_data['promotion_price'], good_data['sale_count'],
                          good_data['comment_count'])
                    try:
                        res = self.s.post(url=self.goods_url, data=good_data)
                    except:
                        time.sleep(5)
                        res = self.s.post(url=self.goods_url, data=good_data)
                    return {'success': True, 'res': res}
                except Exception as e:
                    return {'success': False,
                            'message': "行号 {}, 产品爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e))}

    def save_taobao_data(self, response):
        # time.sleep(2)
        choice = "1"
        try:
            pass
            # res = self.selenium_code()
            # 休息会吧
            # if not res['success']:
            #     choice = input('出现验证码 自动验证失败 请手动验证，请输入您的选择：1.通过 2.未通过')
        except:
            pass
        finally:
            if choice == '1':
                try:
                    item = TaobaoItem()
                    item['original_price'] = self.browser.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').get_attribute('innerText').strip()
                    try:
                        item['promotion_price'] = self.browser.find_element_by_xpath(
                            '//*[@id="J_PromoPriceNum"]').get_attribute('innerText').strip()
                    except:
                        item['promotion_price'] = ''
                    detail_price = sku_price_func(self.browser, 8)

                    ele = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]')
                    self.browser.execute_script("arguments[0].scrollIntoView();", ele)
                    item['detail_sku'] = json.dumps(detail_price)
                    item['title'] = self.browser.find_element_by_xpath('//h3[@class="tb-main-title"]').get_attribute(
                        'innerText').strip()
                    service = self.browser.find_elements_by_xpath('//dt[contains(text(),"承诺")]/following-sibling::dd/a')
                    item['service'] = ','.join([i.get_attribute('innerText') for i in service])
                    try:
                        reputation = self.browser.find_elements_by_xpath('//dd[contains(@class,"tb-rate-")]/a')
                        if not reputation:
                            reputation = self.browser.find_elements_by_xpath(
                                '//li[@class="shop-service-info-item"]//em')
                        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                            reputation[0].get_attribute('innerText').strip(),
                            reputation[1].get_attribute('innerText').strip(),
                            reputation[2].get_attribute('innerText').strip())
                    except:
                        item['reputation'] = ''
                    try:
                        if not item['reputation']:
                            reputation = self.browser.find_elements_by_xpath(
                                '//li[@class="shop-service-info-item"]//em')
                            item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                                reputation[0].get_attribute('innerText').strip(),
                                reputation[1].get_attribute('innerText').strip(),
                                reputation[2].get_attribute('innerText').strip())
                    except:
                        pass
                    try:
                        item['comment_count'] = self.browser.find_element_by_xpath(
                            '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').get_attribute('innerText')
                    except:
                        pass
                    sale_xpath = self.browser.find_element_by_xpath('//*[@id="J_SellCounter"]').get_attribute(
                        'innerText')
                    if sale_xpath:
                        index = sale_xpath.find('万')
                        if index != -1:
                            item['sale_count'] = int(float(sale_xpath[:index]) * 10000)
                        else:
                            if sale_xpath == '-':
                                print("产品爬取失败", response.url, str("验证码"))
                                return {'success': False, 'message': '销量评论数-'}
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
                            d = re.search("\d+", favorite_count_text.get_attribute('innerText'))
                            if d:
                                item['favorite_count'] = int(d.group())
                    except:
                        item['favorite_count'] = 0
                    itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]
                    # detail_list = response.xpath('//ul[@class="attributes-list"]/li//text()').extract()
                    detail_list = self.browser.find_elements_by_xpath('//ul[@class="attributes-list"]/li')
                    detail_str_list = []
                    for j, i in enumerate(detail_list):
                        s = i.get_attribute('innerText').replace(' ', '').replace('\n', '').replace('\r', '').replace(
                            '\t', '').replace('\xa0', '')
                        if s:
                            if s.endswith('：') or s.endswith(':'):
                                detail_str_list.append(s + detail_list[j + 1].get_attribute('innerText'))
                                continue
                            if ':' in s or '：' in s:
                                detail_str_list.append(s)
                    item['detail_str'] = ', '.join(detail_str_list)
                    detail_dict = {}
                    for i in detail_str_list:
                        tmp = re.split('[:：]', i)
                        detail_dict[tmp[0]] = tmp[1].replace('\xa0', '')
                    item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
                    try:
                        img_urls = []
                        img_urls_ele = self.browser.find_elements_by_xpath(
                            '//ul[@id="J_UlThumb"]/li//img')
                        for i in img_urls_ele:
                            img_url = i.get_attribute('src')
                            if not img_url.startswith("http"):
                                img_url = "https:" + img_url
                            img_url = img_url.rsplit('_', 1)[0].replace('_50x50.jpg', '')
                            img_urls.append(img_url)
                        item['cover_url'] = img_urls[0]
                        item['img_urls'] = img_urls
                    except:
                        pass
                    item['site_from'] = 8
                    item['site_type'] = 1
                    if self.key_words[0] in self.price_range_list:
                        price_range = self.price_range_list[self.key_words[0]][0]
                        temp = re.findall('(\d+)', price_range)
                        item['price_range'] = temp[0] + "-" + temp[1] if len(temp) > 1 else temp[0] + '以上'
                    else:
                        item['price_range'] = ''
                    item['out_number'] = itemId
                    # item['cover_url'] = data[0]['cover_url']
                    if self.key_words[0] == '真无线蓝牙耳机 降噪 入耳式':
                        item['category'] = '耳机'
                    else:
                        item['category'] = self.key_words[0]
                    if hasattr(self, 'category'):
                        item['category'] = self.category
                    item['url'] = 'https://item.taobao.com/item.htm?id=' + str(itemId)
                    # impression = self.get_impression(itemId)
                    # item['impression'] = impression
                    good_data = dict(item)
                    print(good_data['original_price'], good_data['promotion_price'], good_data['sale_count'],
                          good_data['comment_count'])
                    try:
                        res = self.s.post(url=self.goods_url, data=good_data)
                    except:
                        time.sleep(10)
                        res = self.s.post(url=self.goods_url, data=good_data)
                    return {'success': True, 'res': res}
                except Exception as e:
                    return {'success': False,
                            'message': "行号 {}, 产品爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e))}

    # 大家印象
    def get_impression(self, out_number):
        impression = ''
        try:
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            try:
                impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers,
                                            verify=False, timeout=10)
            except:
                time.sleep(5)
                impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers,
                                            verify=False, timeout=10)
            rex = re.compile('({.*})')
            impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
            for i in impression_data['tags']['tagClouds']:
                impression += i['tag'] + '(' + str(i['count']) + ')  '
        except:
            pass
        return impression
