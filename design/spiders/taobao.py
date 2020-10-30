import json
import os
import re
import time
import requests
import scrapy
from urllib import parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from design.items import ProduceItem, TaobaoItem, CommentItem
from design.spiders.selenium import SeleniumSpider


class TaobaoSpider(SeleniumSpider):
    name = "taobao"
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.page = 1
        self.data_url = "https://list.tmall.com/search_product.htm?q=%s"
        self.comment_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=1296479913&sellerId=1726473375&order=3&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1603094370130_780&callback=jsonp781'
        self.comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true&t=1603103889422&groupId=&_ksTS=1603103889423_500&callback=jsonp501'
        self.end_page = 50
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.browser.get('https://www.taobao.com/')
        # cookies = self.stringToDict()
        # for i in cookies:
        #     self.browser.add_cookie(i)

    # def stringToDict(self):
    #     '''
    #     将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
    #     :return:
    #     '''
    #     cookies = []
    #     items = self.cookie.(';')
    #     for item in items:
    #         itemDict = {}
    #         key = item.('=')[0].replace(' ', '')
    #         value = item.('=')[1]
    #         itemDict['name'] = key
    #         itemDict['value'] = value
    #         itemDict['path'] = '/'
    #         itemDict['domain'] = '.taobao.com'
    #         itemDict['expires'] = None
    #         cookies.append(itemDict)
    #     return cookies

    def DictToString(self):
        cookies = ''
        items = self.browser.get_cookies()
        for item in items:
            cookies += item['name'] +'='+item['value']+";"
        cookies = cookies[:-1]
        return cookies

    def start_requests(self):
        login_url = 'https://login.taobao.com/member/login.jhtml'
        username = '斌爷爷1058169464'
        password = 'aaa1058169464'
        cookie_file = os.path.join('tmp', '{}@{}.cookie'.format(username, self.name))
        if not os.path.exists(cookie_file):
            self.browser.get(login_url)
            self.browser.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
            self.browser.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
            self.browser.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
            # cookies = self.browser.get_cookies()
            time.sleep(3)
            # fw = open(cookie_file, 'w')
            # fw.write(json.dumps(cookies))
            # fw.close()
        else:
            fr = open(cookie_file, 'r')
            cookies = json.loads(fr.read())
            fr.close()
            for i in cookies:
                self.browser.add_cookie(i)
        yield scrapy.Request(self.data_url % self.key_words, callback=self.parse_list, meta={'usedSelenium': True})

    def parse_list(self, response):
        list_url = response.xpath('//div[@class="product  "]//div[@class="productImg-wrap"]/a/@href').extract()
        # for i in list_url:
        #     yield scrapy.Request("https:"+i, callback=self.parse_detail,meta={'usedSelenium': True})
        yield scrapy.Request("https:" + list_url[0], callback=self.parse_detail, meta={'usedSelenium': True})

    def parse_detail(self, response):
        item = TaobaoItem()
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="tb-detail-hd"]/h1/text()').extract()[0].strip()
        item['original_price'] = response.xpath('//dl[@id="J_StrPriceModBox"]//span/text()').extract()[0]
        item['promotion_price'] = response.xpath('//dl[@id="J_PromoPrice"]//span/text()').extract()[0]
        item['service'] = ','.join(response.xpath('//ul[@class="tb-serPromise"]/li/a/text()').extract())
        reputation = response.xpath('//div[@id="shop-info"]//span[@class="shopdsr-score-con"]//text()').extract()
        item['reputation'] = "描述: %s 服务: %s 物流: %s" % (reputation[0], reputation[1], reputation[2])
        item['turnover'] = response.xpath(
            '//*[@id="J_DetailMeta"]//li[@class="tm-ind-item tm-ind-sellCount"]//span[@class="tm-count"]/text()').extract()
        try:
            item['favorite'] = response.xpath('//span[@id="J_CollectCount"]/text()').extract()[0]
        except:
            item['favorite'] = 0
        detail_list = response.xpath('//div[@id="attributes"]//text()').extract()
        item['detail_str'] = ''
        for i in detail_list:
            s = i.replace(' ','').replace('\n', '').replace('\r', '').replace('\t', '')
            if s:
                item['detail_str'] += s
        # item['img_urls'] = img_urls
        itemId = parse.parse_qs(parse.urlparse(response.url).query)['id'][0]
        headers = {
            'Referer': response.url,
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        elem = WebDriverWait(self.browser, 20, 0.5).until(
            EC.presence_of_element_located(
                (By.ID, 'J_TabBar')
            )
        )
        if elem.is_displayed:
            click = self.browser.find_element_by_xpath('//*[@id="J_TabBar"]')
            click.click()

        impression_ele = self.browser.find_elements_by_xpath('//span[@class="tag-posi"]')
        # impression_res = requests.get(self.comment_impression%itemId,stream=True)
        # rex = re.compile('({.*})')
        # impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        # item['impression'] = ''
        # for i in impression_data['tags']['tagClouds']:
        #      item['impression'] += i['tag']+'('+i['count']+')  '
        item['comment'] = []
        comment_page = 1
        while True:
            comment_res = requests.get(self.comment_url % (itemId, comment_page), headers=headers)
            rex = re.compile('({.*})')
            result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
            for i in  result['rateDetail']['rateList']:
                comment = {}
                comment['type'] = 1 if i['anony'] else 0
                comment['first'] = i['rateContent']
                comment['add'] = i['appendComment']['content'] if i['appendComment'] else ''
                comment['buyer'] = i['displayUserNick']
                comment['style'] = i['pics']
                item['comment'].append(comment)

            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page == pages:
                break
            comment_page += 1
        print(item)

