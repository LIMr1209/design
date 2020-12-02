import json
import os
import re
import time
import requests
import scrapy
from urllib import parse
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider
from selenium import webdriver


class TaobaoSpider(SeleniumSpider):
    name = "taobao"
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }
    goods_url = 'http://127.0.0.1:8002/api/goods/save'
    comment_url = 'http://127.0.0.1:8002/api/comment/save'
    fail_url = []
    max_page = 10

    # goods_url = 'http://opalus-dev.taihuoniao.com/api/goods/save'
    # comment_url = 'http://opalus-dev.taihuoniao.com/api/comment/save'
    # goods_url = 'https://opalus.d3ingo.com/api/goods/save'
    # comment_url = 'https://opalus.d3ingo.com/api/comment/save'

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.price_range = "[459,750]"
        self.page = 1
        self.data_url = 'https://s.taobao.com/search?q={name}&filter=reserve_price{price_range}&s={page_count}'
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.browser.get('https://www.taobao.com/')

    # 更换登陆信息
    def update_cookie(self):
        self.browser.delete_all_cookies() # 删除cookie
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
        time.sleep(5)

    def update_browser(self):
        cookies = self.browser.get_cookies()
        self.browser.quit()
        ua = UserAgent().random
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument("user-agent={}".format(ua))
        # chrome_options.add_argument("--proxy-server=http://1.199.31.96:9999")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 30)  # 指定元素加载超时时间
        self.browser.get('https://www.taobao.com/')  # 必须先请求一下网页，才能添加cookie
        for i in cookies:
            self.browser.add_cookie(i)

    # # 更换动态ip
    # def update_ip(self):
    #     pass

    def start_requests(self):
        self.update_cookie()
        url = self.data_url.format(name=self.key_words, price_range=self.price_range, page_count="0")
        yield scrapy.Request(url, meta={'usedSelenium': True, "page": 1}, callback=self.parse_list)

    def parse_list(self, response):
        page = response.meta['page']
        list_url = response.xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a/@href').extract()
        # list_url = response.xpath('//div[contains(@class,"item J_MouserOnverReq")]//div[@class="pic"]/a/@href').extract()
        yield scrapy.Request("https:" + list_url[0], callback=self.parse_detail,
                             meta={'usedSelenium': True, "list_url": list_url, "page": page})

    def parse_detail(self, response):
        try:
            if "detail.tmall.com" in response.url:
                self.save_tmall_data(response)
            if "item.taobao.com" in response.url:
                self.save_taobao_data(response)
        except Exception as e:
            print(
                "文件 {}".format(e.__traceback__.tb_frame.f_globals["__file__"])
            )  # 文件
            print("行号 {}".format(e.__traceback__.tb_lineno))  # 行号
            print("产品爬取失败", response.url, str(e))
            self.fail_url.append(response.url)
        page = response.meta['page']
        list_url = response.meta['list_url']
        list_url.pop(0)
        # self.update_browser()  # 更换浏览器
        if list_url:
            yield scrapy.Request("https:" + list_url[0], callback=self.parse_detail,
                                 meta={'usedSelenium': True, "list_url": list_url, 'page': page})
        else:
            if self.page < self.max_page:
                self.page += 1
                page_count = str((page - 1) * 44)
                url = self.data_url.format(name=self.key_words, price_range=self.price_range, page_count=page_count)
                yield scrapy.Request(url, meta={'usedSelenium': True}, callback=self.parse_list)

    def save_tmall_data(self, response):
        item = TaobaoItem()
        item['title'] = response.xpath('//div[@class="tb-detail-hd"]/h1/text()').extract()[0].strip()
        item['original_price'] = response.xpath('//dl[@id="J_StrPriceModBox"]//span/text()').extract()[0]
        item['promotion_price'] = response.xpath('//dl[@id="J_PromoPrice"]//span/text()').extract()[0]
        item['service'] = ','.join(response.xpath('//ul[@class="tb-serPromise"]/li/a/text()').extract())
        reputation = response.xpath('//div[@id="shop-info"]//span[@class="shopdsr-score-con"]//text()').extract()
        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (reputation[0], reputation[1], reputation[2])
        sale_xpath = response.xpath(
            '//*[@id="J_DetailMeta"]//li[@class="tm-ind-item tm-ind-sellCount"]//span[@class="tm-count"]/text()').extract()
        if sale_xpath:
            index = sale_xpath[0].find('万')
            if index != -1:
                item['sale_count'] = int(float(sale_xpath[0][:index])*10000)
            else:
                sale_count = re.search('\d+', sale_xpath[0])
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
        detail_list = response.xpath('//div[@id="attributes"]//text()').extract()
        item['detail_str'] = ''
        for i in detail_list:
            s = i.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
            if s:
                item['detail_str'] += s
        try:
            cover_url = response.xpath('//ul[@id="J_UlThumb"]/li//img/@src').extract()[0]
            if not cover_url.startswith == "http":
                cover_url = "https://img.alicdn.com" + cover_url
            cover_url = cover_url.rsplit('_', 1)[0]
        except:
            cover_url = ''
        item['cover_url'] = cover_url
        itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]
        elem = WebDriverWait(self.browser, 20, 0.5).until(
            EC.presence_of_element_located(
                (By.ID, 'J_TabBar')
            )
        )

        # 滚动滚动条 到指定标签位置
        # ele = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]')
        # self.browser.execute_script("arguments[0].scrollIntoView();", ele)
        # if elem.is_displayed:
        #     elem = WebDriverWait(self.browser, 20, 0.5).until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, '//*[@id="J_TabBar"]/li[2]')
        #         )
        #     )
        #     if elem.is_displayed:
        #         click = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]/li[2]')
        #         comment = click.find_element_by_xpath('.//em')
        #         comment_count = comment.text
        #         item['comment_count'] = int(comment_count)
        #         click.click()
        #         elem = WebDriverWait(self.browser, 20, 0.5).until(
        #             EC.presence_of_element_located(
        #                 (By.XPATH, '//span[@class="tag-posi"]')
        #             )
        #         )
        #         if elem.is_displayed:
        #             impression_ele = self.browser.find_elements_by_xpath('//span[@class="tag-posi"]')
        #             impression = []
        #             for i in impression_ele:
        #                 impression.append(i.text)
        #             item['impression'] = "，".join(impression)

        item['site_from'] = 9
        item['site_type'] = 1
        item['price_range'] = self.price_range
        item['out_number'] = itemId
        item['category'] = self.key_words
        item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
        data = dict(item)
        res = requests.post(url=self.goods_url, data=data)
        if res.status_code != 200 or json.loads(res.content)['code']:
            print("产品保存失败", response.url)
            print(json.loads(res.content)['message'])
            self.fail_url.append(response.url)

        # while True:
        #     self.comment_tmall(response)
        #     try:
        #         ele = self.browser.find_element_by_xpath('//a[contains(text(),"下一页>>")]')
        #         if ele:
        #             ele.click()
        #             time.sleep(3)
        #     except:
        #         break

    def save_taobao_data(self, response):
        item = TaobaoItem()
        item['title'] = response.xpath('//h3[@class="tb-main-title"]/text()').extract()[0].strip()
        # item['original_price'] = response.xpath('//dl[@id="J_StrPriceModBox"]//span/text()').extract()[0]
        item['promotion_price'] = response.xpath('//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]/text()').extract()[0]
        item['service'] = ','.join(
            response.xpath('//dt[contains(text(),"承诺")]/following-sibling::dd//text()').extract())
        # reputation = response.xpath('//div[@id="shop-info"]//span[@class="shopdsr-score-con"]//text()').extract()
        # item['reputation'] = "描述: %s 服务: %s 物流: %s" % (reputation[0], reputation[1], reputation[2])
        sale_xpath = response.xpath('//*[@id="J_SellCounter"]/text()').extract()
        if sale_xpath:
            index = sale_xpath[0].find('万')
            if index != -1:
                item['sale_count'] = int(float(sale_xpath[0][:index]) * 10000)
            else:
                sale_count = re.search('\d+', sale_xpath[0])
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
            item['favorite'] = 0
        itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]
        detail_list = response.xpath('//div[@id="attributes"]//text()').extract()
        item['detail_str'] = ''
        for i in detail_list:
            s = i.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
            if s:
                item['detail_str'] += s
        try:
            cover_url = response.xpath('//ul[@id="J_UlThumb"]/li//img/@src').extract()[0]
            if not cover_url.startswith == "http":
                cover_url = "https://img.alicdn.com" + cover_url

            cover_url = cover_url.rsplit('_', 1)[0]
        except Exception as e:
            cover_url = ''
        item['cover_url'] = cover_url
        elem = WebDriverWait(self.browser, 20, 0.5).until(
            EC.presence_of_element_located(
                (By.ID, 'J_TabBar')
            )
        )

        # # 滚动滚动条 直到评论出现
        # ele = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]')
        # self.browser.execute_script("arguments[0].scrollIntoView();", ele)
        #
        # if elem.is_displayed:
        #     elem = WebDriverWait(self.browser, 20, 0.5).until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, '//*[@id="J_TabBar"]/li[2]')
        #         )
        #     )
        #     if elem.is_displayed:
        #         click = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]/li[2]')
        #         comment = click.find_element_by_xpath('.//em')
        #         comment_count = comment.text
        #         item['comment_count'] = int(comment_count)
        #         click.click()
        #         elem = WebDriverWait(self.browser, 20, 0.5).until(
        #             EC.presence_of_element_located(
        #                 (By.XPATH, '//ul[@class="kg-rate-wd-impression tb-r-ubox-bd"]/li/a')
        #             )
        #         )
        #         if elem.is_displayed:
        #             impression_ele = self.browser.find_elements_by_xpath(
        #                 '//ul[@class="kg-rate-wd-impression tb-r-ubox-bd"]/li/a')
        #             impression = []
        #             for i in impression_ele:
        #                 impression.append(i.text)
        #             item['impression'] = "，".join(impression)
                # 评论
        item['site_from'] = 8
        item['site_type'] = 1
        item['price_range'] = self.price_range
        item['out_number'] = itemId
        item['category'] = self.key_words
        item['url'] = 'https://item.taobao.com/item.htm?id=' + str(itemId)
        data = dict(item)
        res = requests.post(url=self.goods_url, data=data)
        if res.status_code != 200 or json.loads(res.content)['code']:
            print("产品保存失败", response.url)
            print(json.loads(res.content)['message'])
            self.fail_url.append(response.url)

        # for i in [1, 0, -1]:
        #     self.browser.find_element_by_xpath('//li[@data-kg-rate-filter-val={}]'.format(str(i))).click()
        #     time.sleep(3)
        #     while True:
        #         if i == 1:
        #             self.comment_taobao(response, comment_kind=0)
        #         elif i == 0:
        #             self.comment_taobao(response, comment_kind=2)
        #         elif i == -1:
        #             self.comment_taobao(response, comment_kind=1)
        #         try:
        #             ele = self.browser.find_element_by_xpath('//li[@class="pg-next"]')
        #             if ele:
        #                 ele.click()
        #                 time.sleep(3)
        #         except:
        #             break

    def comment_taobao(self, response, comment_kind):
        comment_tr = self.browser.find_elements_by_xpath(
            '//div[@class="tb-revbd"]//li[@class="J_KgRate_ReviewItem kg-rate-ct-review-item"]')
        for i in comment_tr:
            style = i.find_elements_by_xpath('.//div[@class="tb-r-info"]')
            style = style[0].get_attribute('outerText')[17:]
            buyer = i.find_element_by_xpath('.//div[@class="from-whom"]/div').get_attribute('outerText')
            content_ele = i.find_elements_by_xpath('.//div[@class="J_KgRate_ReviewContent tb-tbcr-content "]')
            first = content_ele[0].get_attribute('outerText')
            if first == '此用户没有填写评论!':
                first = ''
            add = ''
            if len(content_ele) > 1:
                add = content_ele[1].get_attribute('outerText')[6:]
            data = {
                "style": style,
                "first": first,
                'buyer': buyer,
                'add': add,
                'good_url': response.url,
                'type': comment_kind
            }
            res = requests.post(self.comment_url, data=data)
            if res.status_code != 200 or json.loads(res.content)['code']:
                print("评论保存失败", response.url)
                print(json.loads(res.content)['message'])

    def comment_tmall(self, response):
        comment_tr = self.browser.find_elements_by_xpath('//div[@class="rate-grid"]//tr')
        for i in comment_tr:
            style = i.find_element_by_xpath('.//div[@class="rate-sku"]').get_attribute('outerText')
            style = ''.join([i for i in style if i]).replace('\n', '')
            buyer = i.find_element_by_xpath('.//div[@class="rate-user-info"]').get_attribute('outerText')
            buyer = ''.join([i for i in buyer if i])
            content_ele = i.find_elements_by_xpath('.//div[@class="tm-rate-fulltxt"]')
            first = content_ele[0].get_attribute('outerText')
            if first == '此用户没有填写评论!':
                first = ''
            add = ''
            if len(content_ele) > 1:
                add = content_ele[1].get_attribute('outerText')
            data = {
                "style": style,
                "first": first,
                'buyer': buyer,
                'add': add,
                'good_url': response.url
            }
            res = requests.post(self.comment_url, data=data)
            if res.status_code != 200 or json.loads(res.content)['code']:
                print("评论保存失败", response.url)
                print(json.loads(res.content)['message'])
