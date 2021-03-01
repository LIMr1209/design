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
from selenium.common.exceptions import TimeoutException
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

    def browser_get(self, url):
        try:
            self.browser.get(url)
        except TimeoutException as e:
            self.browser_get(url)

    def start_requests(self):
        # cookies = self.browser.get_cookies()
        # fw = open('tmp/taobao.cookie', 'w')
        # fw.write(json.dumps(cookies))
        # fw.close()self.browser.get
        # self.update_cookie()
        # self.stringToDict()
        # list_url = self.get_list_urls()
        # 爬取失败重新爬取
        list_url = ['https://detail.tmall.com/item.htm?id=562885288405&ad_id=&am_id=&cm_id=140105335569ed55e27b&pm_id=&abbucket=16', 'https://detail.tmall.com/item.htm?id=545415977681&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=566603136571&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610179020245&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=591678331825&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=609344963790&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=590203716935&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=588085110368&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=42941406030&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=617634275558&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=587466668912&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=575856438658&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=586310838669&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=623745650437&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610431871328&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604631887432&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=573998184616&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=566586028937&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=586657988986&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=558458160343&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=588100986739&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=563524511268&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=597214642162&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=628825125261&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=567892656209&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610160633103&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=598803764089&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=41511262182&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=629856523034&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615357225416&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=635160341684&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=603326665249&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=527003710835&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=616274641202&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=599133169628&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=560078892917&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=522069521939&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=623610006698&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=585660086592&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627424684380&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=520479576952&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=546548132396&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=604114137014&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=573913987410&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=612908440923&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=43900458700&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=616621789172&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=605445081317&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=607212617199&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=574077297975&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=41300223424&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631171435433&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=621653264717&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=557781645712&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=522907521937&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615777983456&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=608424962740&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=43005147052&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631506648419&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=531864831585&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=531491291907&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=606347806638&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=557113843415&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=610938237151&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=540302517094&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=585607791455&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=621233900376&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=547119419510&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=629652658539&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=568367163736&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=39666064543&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=538873386136&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=606119809300&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=616198760503&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=621536174763&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=605868483798&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=606285966744&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=633660145532&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=577321739113&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=566331560130&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=17355981854&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=41303150411&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=627950747275&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=615967730999&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=561280315404&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=599324600249&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=539796329591&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=542969445388&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=561242137365&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=581052158104&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=628950781576&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=602976986102&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=530214226087&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=605181600950&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=613213115497&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=562351770450&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=580660480666&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=612348959641&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=539695822101&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=607122012368&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=574398419374&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=626471713111&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=619985573660&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=622615519985&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=554225593302&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=633556330108&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=613371426104&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=565200921209&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=41357298325&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=592427276242&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=634838083413&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=600301558923&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=563316236499&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=25419332338&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=613947499368&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=629972892820&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=542891015052&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=622412764876&ns=1&abbucket=16', 'https://detail.tmall.com/item.htm?id=631484655284&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=42376893597&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=634815899723&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=567936529755&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=573649545958&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=584073535689&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=610242454958&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=560239985130&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=604867476393&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=625031457535&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=637289882162&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=610215438296&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=597474150758&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=626365231762&ns=1&abbucket=16#detail', 'https://detail.tmall.com/item.htm?id=629971501034&ns=1&abbucket=16', 'https://item.taobao.com/item.htm?id=555014683260&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=568440983998&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=616822004473&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=586156816039&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=547211431083&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=588309494609&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=618651604868&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=585336541255&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=585672757253&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=625208421117&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=613868539835&ns=1&abbucket=16#detail', 'https://item.taobao.com/item.htm?id=626963064354&ns=1&abbucket=16#detail']
        self.category = '新风机' # 燃气热水器
        self.error_retry = 1
        yield scrapy.Request(list_url[0], callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True, 'list_url': list_url})

    def get_list_urls(self):
        self.browser_get('https://www.taobao.com/')
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
