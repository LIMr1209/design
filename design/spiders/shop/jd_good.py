# 京东电商
import json
import logging
import re
import time

import requests
import scrapy
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter

from design.items import TaobaoItem
from design.spiders.selenium import SeleniumSpider


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
    # goods_url = 'http://opalus-dev.taihuoniao.com/api/goods/save'
    goods_url = 'https://opalus.d3ingo.com/api/goods/save'
    comment_data_url = 'https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
    fail_url = []
    suc_count = 0

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.price_range = ''
        self.page = 6
        self.max_page = 20
        super(JdSpider, self).__init__(*args, **kwargs)
        # self.browser.switch_to_window(self.browser.window_handles[0])  # 切换新窗口
        print(self.browser.window_handles)
        js = 'window.open("https://www.jd.com/");'
        self.browser.execute_script(js)

    def start_requests(self):
        self.browser.get(
            "https://search.jd.com/Search?keyword=%s&page=%d&s=53" % (
                self.key_words, 1))
        urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
        list_url = []
        for i in urls:
            list_url.append(i.get_attribute('href'))
        yield scrapy.Request(list_url[0], callback=self.parse_detail, meta={'usedSelenium': True,'list_url':list_url})
        # yield scrapy.Request('https://item.jd.com/68579675243.html', callback=self.parse_detail, meta={'usedSelenium': True})

    def parse_detail(self, response):
        item = TaobaoItem()
        item['title'] = self.browser.find_element_by_xpath('//div[@class="sku-name"]').text.strip()
        item['sku_ids'] = ','.join(response.xpath('//div[contains(@id,"choose-attr")]//div[@data-sku]/@data-sku').extract())
        promotion_price = response.xpath('//span[@class="p-price"]/span[2]/text()').extract()[0]
        original_text = response.xpath('//del[@id="page_origin_price" or @id="page_opprice" or @id="page_hx_price"]/text()').extract()
        if original_text:
            item['original_price'] = original_text[0][1:]
        if not 'original_price' in item:
            item['original_price'] = promotion_price
            item['promotion_price'] = ''
        else:
            item['promotion_price'] = promotion_price
        comment_text = response.xpath('//a[contains(@class,"count J-comm")]/text()').extract()
        if comment_text:
            comment_count = comment_text[0]
            index = comment_count.find('万')
            if index != -1:
                item['comment_count'] = int(float(comment_count[:index]) * 10000)
            else:
                comment_count = re.search('\d+', comment_count)
                if comment_count:
                    item['comment_count'] = int(comment_count.group())
        item['category'] = self.key_words
        item['service'] = ','.join(response.xpath('//div[@id="J_SelfAssuredPurchase"]/div[@class="dd"]//a/text()').extract())
        reputation_keys = response.xpath('//span[@class="score-desc"]/text()').extract()
        reputation_values = response.xpath('//span[contains(@class,"score-detail")]/em/text()').extract()
        reputation_list = []
        for i in range(len(reputation_keys)):
            reputation_list.append(reputation_keys[i]+": "+reputation_values[i])
        item['url'] = response.url.replace('http:','https:')
        item['reputation'] =' '.join(reputation_list)
        detail_keys = response.xpath('//dl[@class="clearfix"]/dt/text()').extract()
        detail_values = response.xpath('//dl[@class="clearfix"]/dd/text()').extract()
        detail_dict = {}
        detail_str_list = []
        for i in range(len(detail_keys)):
            detail_str_list.append(detail_keys[i] + ':' + detail_values[i])
            detail_dict[detail_keys[i]] = detail_values[i]
        if not detail_keys:
            detail_list = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li//text()').extract()
            for j, i in enumerate(detail_list):
                s = i.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0',
                                                                                                     '')
                if s.endswith('：') or s.endswith(':'):
                    detail_str_list.append(s + detail_list[j + 1])
                    continue
                if ':' in s or '：' in s:
                    detail_str_list.append(s)
            item['detail_str'] = ', '.join(detail_str_list)
            for i in detail_str_list:
                tmp = re.split('[:：]', i)
                detail_dict[tmp[0]] = tmp[1].replace('\xa0', '')
            item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
        item['detail_dict'] = json.dumps(detail_dict, ensure_ascii=False)
        item['detail_str'] = ', '.join(detail_str_list)
        item['price_range'] = self.price_range
        itemId = re.findall('\d+',response.url)[0]
        item['out_number'] = itemId
        item['site_from'] = 11
        item['site_type'] = 1
        img_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'http://img10.360buyimg.com/n12/%s' % img_urls[i]
        item['cover_url'] = img_urls[0]
        item['img_urls'] = ','.join(img_urls)
        good_data = dict(item)

        ua = UserAgent().random
        headers = {
            'Referer': 'https://item.jd.com/%s.html' % itemId,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Cookie': 'JSESSIONID=068CE69BEB8E77E7FF7D415202926236.s1; Path=/',
        }
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        s.mount('https://', HTTPAdapter(max_retries=5))
        url = self.comment_data_url % (itemId,0)
        comment_res = s.get(url, headers=headers, verify=False, timeout=10)
        rex = re.compile('({.*})')
        result = json.loads(rex.findall(comment_res.text)[0])
        good_data['positive_review'] = result['productCommentSummary']['goodCount']
        good_data['comment_count'] = result['productCommentSummary']['commentCount']
        impression = ''
        for j in result['hotCommentTagStatistics']:
            impression += j['name'] + '(' + str(j['count']) + ')  '
        good_data['impression'] = impression
        print(good_data)
        res = s.post(url=self.goods_url, data=good_data)
        if res.status_code != 200 or json.loads(res.content)['code']:
            logging.error("产品保存失败" + response.url)
            logging.error(json.loads(res.content)['message'])
            self.fail_url.append(response.url)
        else:
            self.suc_count += 1
        list_url = response.meta['list_url']
        list_url.pop(0)
        time.sleep(3)
        if list_url:
            yield scrapy.Request(list_url[0], meta={'usedSelenium': True, "list_url": list_url},
                                 callback=self.parse_detail,
                                 dont_filter=True)
        else:
            self.page += 1
            if self.page <= self.max_page:
                self.browser.get(
                    "https://search.jd.com/Search?keyword=%s&page=%d&s=53" % (
                        self.key_words, self.page))
                urls = self.browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
                list_url = []
                for i in urls:
                    list_url.append(i.get_attribute('href'))
                yield scrapy.Request(list_url[0], callback=self.parse_detail,
                                     meta={'usedSelenium': True, 'list_url': list_url})
