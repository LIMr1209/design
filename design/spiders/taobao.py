import json
import scrapy
from design.items import ProduceItem, TaobaoItem
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
        self.cookie = "tg=0; cna=zasMF12t3zoCATzCuQKpN3kO; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; thw=cn; enc=hhk8t%2B%2Bkpl2xLE0wC5J9lH0S9A81kjr1zit1l9%2B956QkQ8CH2AfazGIkEVic1u9A7tiLbGrsuDqVPO4%2BeLizug%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; miid=149403541520371257; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; mt=ci=4_1; _samesite_flag_=true; cookie2=167e49f0bd5118e188156d5057cfec8e; t=2e09211d408c4672133f88cd3b7a57c1; _tb_token_=fe9e3f87be7eb; sgcookie=E100EyPmsidazidttKDDTHu%2FibtACMe46spRMTt3W%2BADBATC%2B6WLbLTov4t02JZjcnkOXrprMqpLyUxwnE%2FJgBWzGA%3D%3D; uc3=id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D&lg2=UIHiLt3xD8xYTw%3D%3D&vt3=F8dCufeOb%2FP7apna8eo%3D; csg=229583fc; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; skt=787d3e4dbad0f601; existShop=MTYwMTAxMjg3MQ%3D%3D; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSdoC3JDBP2R&nk4=0%400AdtZS03tnds0llDWCRcSihqN1j2LxKsh6Ub; _cc_=U%2BGCWk%2F7og%3D%3D; v=0; _m_h5_tk=2912fb3914db3529b80e1a21542a0cb1_1601194943350; _m_h5_tk_enc=40a0dc6ec266359f8ea39992157df0bd; xlly_s=1; uc1=cookie21=VFC%2FuZ9aiKCaj7AzMHh1&pas=0&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&existShop=false&cookie14=Uoe0bHb9FOaMGg%3D%3D; l=eBjqXoucQKR1CqKDBOfwnurza77tKIRA_uPzaNbMiOCP951pX6qPWZzYioT9CnGVh65wR3RSn5QgBeYBqIA7kOiEIosM_6Hmn; tfstk=cJQOBJGPuJ2MLiOdaGEHGg7t5qVhZE09Hf9rk7UVgmIjyCgAiJ7lyZx0fQH9JWC..; isg=BAEBe4tLOiA8vlfOlaVbt8YREE0bLnUgJ3Q-rGNWu4hLSiEcq3-98L1ALL4MxQ1Y"
        self.data_url = "https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%s&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest"
        self.end_page = 50
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.browser.get('https://www.taobao.com/')
        cookies = self.stringToDict()
        for i in cookies:
            self.browser.add_cookie(i)

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
            itemDict['domain'] = '.taobao.com'
            itemDict['expires'] = None
            cookies.append(itemDict)
        return cookies

    def start_requests(self):
        # for i in range(self.page, self.end_page):
        yield scrapy.Request(self.data_url % self.key_words, callback=self.parse_list,meta={'usedSelenium': True} )


    def parse_list(self, response):
        list_url = response.xpath('//div[@class="item J_MouserOnverReq  "]//div[@class="pic"]/a/@href').extract()
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
        item['reputation'] = ','.join(response.xpath('//div[@id="side-shop-info"]//div[@class="main-info"]/div[@class="shopdsr-item"]').extract())
        item[''] = response.xpath('//span[@id="J_CollectCount"]/text()').extract()[0]
        item['img_urls'] = img_urls
        yield item
