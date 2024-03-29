import logging
import random
import re
from urllib.parse import urlencode
import json

import requests
import time

from pydispatch import dispatcher
from requests.adapters import HTTPAdapter
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC

from design.utils.antiContent_Js import js
import execjs
import scrapy
from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider

# 获取 sku 价格样式
def sku_price_func(browser, site_from):
    page_source = browser.page_source
    rex = re.compile('("attribute.*?,)"skuID')
    res_replace = re.findall(rex, page_source)
    for i in res_replace:
        page_source = page_source.replace(i, '')
    rex = re.compile('skus.*?(\[{.*}]),"thumbUrl')
    res = re.findall(rex, page_source)
    detail_price = ''
    if res:
        sku_price = json.loads(res[0])
        detail_price = []
        for j in sku_price:
            original_price = j['normalPrice']
            promotion_price = j['groupPrice']
            skuid = str(j['skuId'])
            cover_url = j['thumbUrl']
            style = {}
            for z in j['specs']:
                if z:
                    style[z['spec_key']] = z['spec_value']
            detail_price.append({
                'skuid': skuid,
                'cover_url': cover_url,
                'promotion_price': promotion_price,
                'original_price': original_price,
                'style': style
            })
    return detail_price


class PddSpider(SeleniumSpider):
    # 爬虫启动时间
    name = 'pdd'
    allowed_domains = ['yangkeduo.com']
    # 商品信息API
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'ERROR',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words.split(',')
        self.price_range_list = {
            '吹风机': ['price,459,750', 'price,751,999', 'price,1000,-1'],
            '真无线蓝牙耳机 降噪 入耳式': ['price,300,900', 'price,900,3000'],
        }
        self.page = 4
        self.max_price_page = 10
        self.max_page = 20
        self.pdd_accessToken_list = []
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.settings = get_project_settings()
        if len(self.settings['PDD_ACCESS_TOKEN_LIST']) != len(self.settings['PDD_VERIFY_AUTH_TOKEN']):
            logging.error('pdd用户信息长度不匹配')
            return
        for i, j in enumerate(self.settings['PDD_ACCESS_TOKEN_LIST']):
            self.pdd_accessToken_list.append({
                'AccessToken': j,
                'VerifyAuthToken': self.settings['PDD_VERIFY_AUTH_TOKEN'][i]
            })
        self.goods_url = self.settings['OPALUS_GOODS_URL']
        self.search_url = 'http://apiv3.yangkeduo.com/search?'
        self.fail_url = {}
        self.suc_count = 0
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        }
        super(PddSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("http://yangkeduo.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口

    def except_close(self):
        logging.error("待爬取关键词:")
        logging.error(self.key_words)
        logging.error('页码')
        logging.error(self.page)
        logging.error('价位档')
        logging.error(self.price_range_list)
        logging.error('爬取失败')
        logging.error(self.fail_url)

    def fail_url_save(self, response):
        if hasattr(self,'error_retry'):
            if self.category in self.fail_url:
                self.fail_url[self.category].append(response.url)
            else:
                self.fail_url[self.category] = [response.url]
        else:
            if self.key_words[0] in self.fail_url:
                self.fail_url[self.key_words[0]].append(response.url)
            else:
                self.fail_url[self.key_words[0]] = [response.url]

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

    # 切换登陆信息
    def switch_token(self):
        token = random.choice(self.pdd_accessToken_list)
        self.headers['AccessToken'] = token['AccessToken']
        self.headers['VerifyAuthToken'] = token['VerifyAuthToken']
        # 切换浏览器cookie
        itemDict = {}
        itemDict['name'] = 'PDDAccessToken'
        itemDict['value'] = token['AccessToken']
        itemDict['path'] = '/'
        itemDict['domain'] = 'yangkeduo.com'
        itemDict['expires'] = None
        self.browser.delete_cookie('PDDAccessToken')
        self.browser.delete_cookie('pdd_user_id')
        self.browser.delete_cookie('pdd_user_uin')
        self.browser.add_cookie(itemDict)

    def start_requests(self):
        """
        请求搜索页
        """
        self.switch_token()
        url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words[0]
        yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})
        # yield scrapy.Request('http://yangkeduo.com/goods.html?goods_id=194785923304>', callback=self.parse_detail,
        #                      meta={'usedSelenium': True})

    def get_parameters(self, response):
        """
        获取参数：list_id, flip, anti_content
        """
        list_id = re.findall('"listID":"(.*?)"', response.text, re.S)[0]
        flip = re.findall('"flip":"(.*?)"', response.text, re.S)[0]
        ctx = execjs.compile(js)
        anti_content = ctx.call('result', response.url)
        self.data = {
            'gid': '',
            'item_ver': 'lzqq',
            'source': 'index',
            'search_met': 'history',
            'requery': '0',
            'list_id': list_id,
            'sort': 'default',
            'filter': '',
            'track_data': 'refer_page_id,10002_1600936236168_2wdje7q7ue;refer_search_met_pos,0',
            'q': self.key_words[0],
            'page': self.page,
            'size': '50',
            'flip': flip,
            'anti_content': anti_content,
            'pdduid': '9575597704'
        }
        if self.key_words[0] in self.price_range_list:
            self.data['filter'] = self.price_range_list[self.key_words[0]][0]
        yield scrapy.Request(url=self.search_url + urlencode(self.data),
                             headers=self.headers,
                             callback=self.parse_list,
                             dont_filter=True)

    def parse_list(self, response):
        """
        获取商品信息
        """
        items = json.loads(response.text)['items']
        items_list = []
        for item in items:
            item_data = TaobaoItem()
            item_data['cover_url'] = item['item_data']['goods_model']['thumb_url']
            title = item['item_data']['goods_model']['goods_name']
            # if self.key_words[0] not in title:
            #     logging.error('商品不属于此分类 标题:%s 分类:%s' % (title, self.key_words[0]))
            #     continue
            item_data['title'] = title
            item_data['category'] = self.key_words[0]
            item_data['original_price'] = str(item['item_data']['goods_model']['normal_price'] / 100)
            item_data['promotion_price'] = str(item['item_data']['goods_model']['price'] / 100)
            item_data['out_number'] = item['item_data']['goods_model']['goods_id']
            if self.key_words[0] in self.price_range_list:
                price_range_temp = self.price_range_list[self.key_words[0]][0].split(',')
                if price_range_temp[2] == '-1':
                    price_range = price_range_temp[1]+'以上'
                else:
                    price_range = price_range_temp[1] + '-' + price_range_temp[2]
            else:
                price_range = ''
            item_data['price_range'] = price_range
            item_data['sale_count'] = item['item_data']['goods_model']['sales']
            item_data['site_from'] = 10
            item_data['site_type'] = 1
            # url = 'http://yangkeduo.com/{}'.format(item['item_data']['goods_model']['link_url'])
            item_data['url'] = 'http://yangkeduo.com/goods.html?goods_id=%s' % item['item_data']['goods_model'][
                'goods_id']
            items_list.append(item_data)
        self.switch_token()
        # time.sleep(random.randint(3, 5))
        if not items_list:
            self.key_words.pop(0)
            self.page = 1
            if self.key_words:
                url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words[0]
                yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})
        else:
            yield scrapy.Request(items_list[0]['url'], meta={'usedSelenium': True, "items_list": items_list},
                                 callback=self.parse_detail,
                                 dont_filter=True)

    def parse_detail(self, response):
        choice = '1'
        try:
            verify_tag = WebDriverWait(self.browser, 1, 0.5).until(
                EC.presence_of_element_located(
                    (By.ID, 'intelVerify')
                )
            )
            if verify_tag.is_displayed:
                self.logger.error('发现划线验证，请手动验证并确认验证结果')
                choice = input('请输入您的选择：1，通过 2. 未通过')
        except:
            pass
        if choice == "1":
            items_list = response.meta['items_list']
            item = items_list.pop(0)
            res = self.get_good_data(item, response)
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
            # time.sleep(random.randint(9, 15))
            self.switch_token()
            if items_list:
                yield scrapy.Request(items_list[0]['url'], meta={'usedSelenium': True, "items_list": items_list},
                                     callback=self.parse_detail,
                                     dont_filter=True)
            else:
                # time.sleep(random.randint(3, 5))
                print(self.fail_url)
                self.page += 1
                if self.key_words[0] in self.price_range_list:
                    page = self.max_price_page
                else:
                    page = self.max_page
                if self.page <= page:
                    self.data['page'] = self.page
                    yield scrapy.Request(url=self.search_url + urlencode(self.data),
                                         headers=self.headers,
                                         callback=self.parse_list,
                                         dont_filter=True)
                else:
                    if self.key_words[0] in self.price_range_list and len(
                            self.price_range_list[self.key_words[0]]) > 1:
                        self.price_range_list[self.key_words[0]].pop(0)
                    else:
                        self.key_words.pop(0)
                    self.page = 1
                    if self.key_words:
                        url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words[0]
                        yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})


    def get_good_data(self, item, response):
        try:
            while True:
                if "原商品已售罄，为你推荐相似商品" in self.browser.page_source:
                    time.sleep(600)
                    self.browser.refresh()
                    # self.fail_url.append(self.browser.current_url)
                    # return {'success': False, 'message': '商品详情反爬'}
                else:
                    break
            img_urls = []
            try:
                data = re.findall('"topGallery":(\[.*?\])', self.browser.page_source)[0]
                data = json.loads(data)
                for i in data:
                    img_urls.append(i['url'])
            except:
                self.browser.refresh()
                img_ele = self.browser.find_elements_by_xpath('//li[contains(@class,"islider-html")]/img')
                for i in img_ele:
                    img_urls.append(i.get_attribute('src'))
            item['img_urls'] = ','.join(img_urls)
            detail_price = sku_price_func(self.browser, 10)
            detail_price = sorted(detail_price, key=lambda x: x["original_price"])
            service_list = self.browser.find_elements_by_xpath('//div[@class="fsI_SU5H"]/div')
            service_list = [i.text for i in service_list if i.text]
            item['service'] = ','.join(service_list)
            if detail_price:
                item['detail_sku'] = json.dumps(detail_price)
                item['original_price'] = detail_price[0]['original_price'] + '-' + detail_price[-1]['original_price']
                item['promotion_price'] = detail_price[0]['promotion_price'] + '-' + detail_price[-1]['promotion_price']

            try:
                comment_text = self.browser.find_element_by_xpath('//div[@class="ccIhLMdm"]')
                comment_text = re.findall('商品评价\((.*)\)', comment_text.text)[0]
                index = comment_text.find('万')
                if index != -1:
                    item['comment_count'] = int(float(comment_text[:index]) * 10000)
                else:
                    comment_count = re.search('\d+', comment_text)
                    item['comment_count'] = int(comment_count.group())
            except:
                item['comment_count'] = 0
            detail_keys = self.browser.find_elements_by_xpath('//div[@class="_8rUS_gSm"]/div[1]')
            detail_values = self.browser.find_elements_by_xpath('//div[@class="_8rUS_gSm"]/div[2]')
            detail_dict = {}
            detail_str_list = []
            for i in range(len(detail_keys)):
                detail_str_list.append(detail_keys[i].text + ':' + detail_values[i].text)
                detail_dict[detail_keys[i].text] = detail_values[i].text
            item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
            item['detail_str'] = ', '.join(detail_str_list)
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

