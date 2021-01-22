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
                            '//dl[@id="J_StrPriceModBox"]//span').text
                    except:
                        original_price = browser.find_element_by_xpath(
                            '//span[@class="tm-price"]').text
                    try:
                        promotion_price = browser.find_element_by_xpath(
                            '//dl[@id="J_PromoPrice"]//span').text
                    except:
                        promotion_price = ''
                else:
                    original_price = browser.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').text.strip()
                    try:
                        promotion_price = browser.find_element_by_xpath(
                            '//*[@id="J_PromoPriceNum"]').text.strip()
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
    t = 0.2
    # 初速度
    v = 0

    while current < distance:
        if current < mid:
            # 加速度为2
            a = 60
        else:
            # 加速度为-2
            a = -100
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
    name = "taobao"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.page = 3
        self.max_page = 15
        self.max_price_page = 7  # 价格区间的爬10页
        self.price_range_list = {
            '吹风机': ['[459,750]', '[751,999]', '[1000,]'],
            '真无线蓝牙耳机 降噪 入耳式': ['[300, 900]', '[900,3000]'],
        }
        self.key_words = ['早餐机', '酸奶机', '电火锅', '豆芽机', '美妆冰箱', '美发梳', '除螨仪', '筋膜枪', '脱毛仪, '
                          '颈椎按摩仪', '扫地机器人', '电动蒸汽拖把','挂烫机', '烘衣机', '烤箱', '电饭煲', '加湿器', '微波炉',
                          '吸尘器', '取暖器', '卷/直发器', '豆浆机', '烤饼机','绞肉机', '净水器', '电压力锅', '洗碗机'
                          ]
        # self.key_words = key_words.split(',')
        self.fail_url = []
        self.suc_count = 0
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.goods_url = self.setting['OPALUS_GOODS_URL']
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.search_url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q={name}&filter=reserve_price{price_range}&s={page_count}&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
        self.cookie = 'hng=CN%7Czh-CN%7CCNY%7C156; t=27342fccaf0252611c51fc03fa4e7ac6; enc=MIfEinE%2BUqe%2FrOAJ4kSL2sf8sPaGqMfQhs3fJI6jVi9whtay9lqef7PafAH8YbF%2Bpb%2FPiEz6i%2FJP%2B7yEO0dpYA%3D%3D; _tb_token_=f353e3600a381; cookie2=1e1329c204b483965c50f4aea175989c; xlly_s=1; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; cna=zasMF12t3zoCATzCuQKpN3kO; uc1=existShop=false&cookie21=UtASsssmeW6lpyd%2BB%2B3t&cookie14=Uoe0az9h5Ti4KA%3D%3D&pas=0&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D; uc3=lg2=UIHiLt3xD8xYTw%3D%3D&vt3=F8dCuf2CSp7DjbEF1as%3D&id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSdvtCI6XCk%2F&nk4=0%400AdtZS03tnds0llDWCRcSihqN1jxbD1O2opb; sgcookie=E100PSo4OpJklR8obNtKBryUufO195A5YSzyXhka2trDZeXqTdHNTDWmqifymuuq1627cAyn3cQnqskk9ztKGfP43g%3D%3D; csg=2a17af03; pnm_cku822=098%23E1hv%2F9vUvbpvUvCkvvvvvjiWP2dyQjnmn2dwgj1VPmPO6jr8RFswzj3WPFSv0jYURvhvCvvvvvvUvpCWCRbXvvaF9W2%2BFfmtEpcZTWexRdIAcUmxfwofd56Ofa3lKbh6UxWnSXVxI2iI27zh1j7ZHkx%2F1RBlYb8rwZXlJXxreC9aWXxr1WmK5I9CvvOUvvVvJhTIvpvUvvmvR0nopE4gvpvIvvvvvhCvvvvvvUUvphvUbpvv99Cvpv32vvmmvhCvmWIvvUUvphvUA9vCvvOvCvvvphvRvpvhvv2MMTOCvvpvvUmm; _m_h5_tk=b89879a97398b54808462f75f2281c05_1606972762508; _m_h5_tk_enc=27f9ec8ed65873154cb5f358e7cc2baf; tfstk=cplGB7MRRAy_J-2nFCNsruEv8P-dZrtabjltTXaIUF2atkGFigBFUcbp-koiMt1..; l=eBQJ2fCIQDOlzshQBOfZlurza77OhIRYouPzaNbMiOCPOT5e5omlWZROa_TwCnGVh6cBR3oVpXaaBeYBqhvQ5O95a6Fy_pHmn; isg=BPv7i6eNIMq3nB1mTJyyKlytit9lUA9SVto5X-24ufoRTBsudSELooqGZuwC6mdK; cq=ccp%3D1'
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
        elem = WebDriverWait(self.browser, 5, 0.5).until(
            EC.presence_of_element_located(
                (By.ID, 'sufei-dialog-content')
            )
        )
        if elem.is_displayed:
            iframe = self.browser.find_element_by_id('sufei-dialog-content')  # 找到“嵌套”的iframe
            self.browser.switch_to.frame(iframe)
            button = self.browser.find_element_by_xpath('//span[@class="nc_iconfont btn_slide"]')
            action = ActionChains(self.browser)
            action.click_and_hold(button).perform()
            tracks = get_track(300)
            for x in tracks:
                action.move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.5)
        self.browser.switch_to_default_content()

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
        page_count = str((self.page - 1) * 44)
        if self.key_words[0] in self.price_range_list:
            url = self.search_url.format(name=self.key_words[0],
                                         price_range=self.price_range_list[self.key_words[0]][0], page_count=page_count)
        else:
            url = self.search_url.format(name=self.key_words[0], price_range='', page_count=page_count)
        yield scrapy.Request(url, meta={'usedSelenium': True}, callback=self.parse_list, dont_filter=True)
        # yield scrapy.Request(
        #     'https://item.taobao.com/item.htm?id=634753807151&ns=1&abbucket=6#detail',
        #     callback=self.parse_detail, dont_filter=True, meta={'usedSelenium': True})

    def parse_list(self, response):
        list_url = response.xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a/@href').extract()
        if list_url:
            yield scrapy.Request("https:" + list_url[0], callback=self.parse_detail, dont_filter=True,
                                 meta={'usedSelenium': True, 'list_url': list_url})

    def parse_detail(self, response):
        # time.sleep(4)
        if "detail.tmall.com" in response.url:
            res = self.save_tmall_data(response)
        if "item.taobao.com" in response.url:
            res = self.save_taobao_data(response)
        if not res['success']:
            self.fail_url.append(response.url)
            logging.error(res['message'])
        else:
            respon = res['res']
            if respon.status_code != 200 or json.loads(respon.content)['code']:
                logging.error("产品保存失败" + response.url)
                logging.error(json.loads(respon.content)['message'])
                self.fail_url.append(response.url)
            else:
                self.suc_count += 1
        list_url = response.meta['list_url']
        list_url.pop(0)
        if list_url:
            yield scrapy.Request('https:' + list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True, "list_url": list_url}, dont_filter=True, )
        else:
            if self.key_words[0] in self.price_range_list:
                page = self.max_price_page
            else:
                page = self.max_page
            if self.page < page:
                self.page += 1
            else:
                self.page = 1
                if self.key_words[0] in self.price_range_list and len(self.price_range_list[self.key_words[0]]) > 1:
                    self.price_range_list[self.key_words[0]].pop(0)
                else:
                    self.key_words.pop(0)
            if self.key_words:
                page_count = str((self.page - 1) * 44)
                if self.key_words[0] in self.price_range_list:
                    url = self.search_url.format(name=self.key_words[0],
                                                 price_range=self.price_range_list[self.key_words[0]][0],
                                                 page_count=page_count)
                else:
                    url = self.search_url.format(name=self.key_words[0], price_range='', page_count=page_count)
                yield scrapy.Request(url, meta={'usedSelenium': True}, callback=self.parse_list, dont_filter=True)

    def save_tmall_data(self, response):
        # time.sleep(2)
        choice = "1"
        try:
            code_ele = self.browser.find_element_by_id('sufei-dialog-content')
            if code_ele:
                # choice = input('出现验证码 请手动验证，请输入您的选择：1.通过 2.未通过')
                close_ele = self.browser.find_element_by_id('sufei-dialog- close')
                if close_ele:
                    close_ele.click()
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
                        '//div[@class="tb-detail-hd"]/h1').text.strip()
                    service = self.browser.find_elements_by_xpath('//ul[@class="tb-serPromise"]/li/a')
                    item['service'] = ','.join([i.text for i in service])
                    try:
                        reputation = self.browser.find_elements_by_xpath('//span[@class="shopdsr-score-con"]')
                        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (
                            reputation[0].text.strip(), reputation[1].text.strip(), reputation[2].text.strip())
                    except:
                        pass
                    try:
                        item['comment_count'] = self.browser.find_element_by_xpath(
                            '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').get_attribute('innerText')
                    except:
                        pass
                    sale_xpath = self.browser.find_element_by_xpath(
                        '//*[@id="J_DetailMeta"]//li[@class="tm-ind-item tm-ind-sellCount"]//span[@class="tm-count"]').get_attribute('innerText')
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
                    item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
                    impression = self.get_impression(itemId)
                    item['impression'] = impression
                    good_data = dict(item)
                    print(good_data)
                    try:
                        res = self.s.post(url=self.goods_url, data=good_data)
                    except:
                        time.sleep(10)
                        res = self.s.post(url=self.goods_url, data=good_data)
                    return {'success': True, 'res': res}
                except Exception as e:
                    return {'success': False,
                            'message': "行号 {}, 产品爬取失败 {} {}".format(e.__traceback__.tb_lineno, response.url, str(e))}

    def save_taobao_data(self, response):
        # time.sleep(2)
        choice = "1"
        try:
            # 登录iframe
            code_ele = self.browser.find_element_by_id('sufei-dialog-content')
            if code_ele:
                # choice = input('出现验证码 请手动验证，请输入您的选择：1.通过 2.未通过')
                close_ele = self.browser.find_element_by_id('sufei-dialog- close')
                if close_ele:
                    close_ele.click()
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
                    item['title'] = self.browser.find_element_by_xpath('//h3[@class="tb-main-title"]').text.strip()
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
                            '//ul[@id="J_TabBar"]//em[@class="J_ReviewsCount"]').get_attribute('innerText')
                    except:
                        pass
                    sale_xpath = self.browser.find_element_by_xpath('//*[@id="J_SellCounter"]').get_attribute('innerText')
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
                    item['url'] = 'https://item.taobao.com/item.htm?id=' + str(itemId)
                    impression = self.get_impression(itemId)
                    item['impression'] = impression
                    good_data = dict(item)
                    print(good_data)
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
                time.sleep(10)
                impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers,
                                            verify=False, timeout=10)
            rex = re.compile('({.*})')
            impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
            for i in impression_data['tags']['tagClouds']:
                impression += i['tag'] + '(' + str(i['count']) + ')  '
        except:
            pass
        return impression
