import re
from urllib.parse import urlencode
import json

import execjs
import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class PddSpider(SeleniumSpider):
    # 爬虫启动时间
    name = 'pdd'
    allowed_domains = ['yangkeduo.com']
    # 商品信息API
    search_url = 'http://apiv3.yangkeduo.com/search?'
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'AccessToken': 'VUYECGCH4CUCRUN3QHEU2KCRX2HJ53AAMGFGSUOLNIXCLEBMB7WA1128855',
        'VerifyAuthToken': '1GOiKCrZqy8OtXkhOmD-nQ5a78a1501eec267f6'
    }

    def __init__(self, key_words=None, *args, **kwargs):
        self.key_words = key_words
        self.cookie = "api_uid=rBTZeV9pkS+MZwBRTyx6Ag==; _nano_fp=XpEoX0mjXqgon5TxXC_vzR~BXj_x6NvFC8UiAPB2; ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F85.0.4183.102%20Safari%2F537.36; webp=1; chat_list_rec_list=chat_list_rec_list_oPtfEa; msec=1800000; quick_entrance_click_record=20200924%2C1; PDDAccessToken=VUYECGCH4CUCRUN3QHEU2KCRX2HJ53AAMGFGSUOLNIXCLEBMB7WA1128855; pdd_user_id=9575597704; pdd_user_uin=DM2PLOFMXZMZ4YU45DJ5BRMRDQ_GEXDA; JSESSIONID=2D0AE5F2A5904F8ACDFF833B97AF0423; pdd_vds=gaLLNIbOEybboytPobQObtmGQOQiQPynyPOnaiaPPQPNtImLIGQGEiGNtNan"
        self.browser.get('http://yangkeduo.com/')
        cookies = self.stringToDict()
        for i in cookies:
            self.browser.add_cookie(i)
        super(PddSpider, self).__init__(*args, **kwargs)

    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        cookies = []
        items = self.cookie.split(';')
        for item in items:
            itemDict = {}
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict['name'] = key
            itemDict['value'] = value
            itemDict['path'] = '/'
            itemDict['domain'] = 'yangkeduo.com'
            itemDict['expires'] = None
            cookies.append(itemDict)
        return cookies


    def start_requests(self):
        """
        请求搜索页
        """
        url = 'http://yangkeduo.com/search_result.html?search_key=' + self.key_words
        yield scrapy.Request(url, callback=self.get_parameters, meta={'usedSelenium': True})

    def get_parameters(self, response):
        """
        获取参数：list_id, flip, anti_content
        """
        list_id = re.findall('"listID":"(.*?)"', response.text, re.S)[0]
        flip = re.findall('"flip":"(.*?)"', response.text, re.S)[0]
        # with open('./utils/anti_content.js', 'r', encoding='gbk') as f:
        #     js = f.read()
        from design.utils.antiContent_Js import js
        for page in range(1, 20):
            ctx = execjs.compile(js)
            anti_content = ctx.call('result', response.url)
            # anti_content = execjs.compile(js).call('get_anti', response.url)
            data = {
                'gid': '',
                'item_ver': 'lzqq',
                'source': 'index',
                'search_met': 'history',
                'requery': '0',
                'list_id': list_id,
                'sort': 'default',
                'filter': '',
                'track_data': 'refer_page_id,10002_1600936236168_2wdje7q7ue;refer_search_met_pos,0',
                'q': self.key_words,
                'page': page,
                'size': '50',
                'flip': flip,
                'anti_content': anti_content,
                'pdduid': '9575597704'
            }
            yield scrapy.Request(url=self.search_url + urlencode(data),
                          headers=self.headers,
                          callback=self.parse_list,
                          dont_filter=True)

    def parse_list(self, response):
        """
        获取商品信息
        """
        if response:
            items = json.loads(response.text)['items']
            for item in items:
                if 'link_url' in item['item_data']['goods_model']:
                    yield scrapy.Request('http://yangkeduo.com/{}'.format(item['item_data']['goods_model']['link_url']), meta={'usedSelenium': True}, callback=self.parse_detail, dont_filter=True)

        else:
            self.logger.debug("No data obtained!")

    def parse_detail(self, response):
        item = ProduceItem()
        data = re.findall('"topGallery":(\[.*?\])', response.text)[0]
        data = json.loads(data)
        img_urls = []
        for i in data:
            img_urls.append(i['url'])
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        item['channel'] = 'pdd'
        yield item
