import json
import scrapy
from design.items import ProduceItem
from design.spiders.selenium import SeleniumSpider


class S1688Spider(SeleniumSpider):
    name = "s1688"
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
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
        self.page = 2
        self.cookie = 'hng=CN%7Czh-CN%7CCNY%7C156; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; cna=zasMF12t3zoCATzCuQKpN3kO; h_keys="%u62c9%u6746%u7bb1"; ali_ab=218.108.42.174.1600752653118.9; ali_apache_track=c_mid=b2b-26715147234e376|c_lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464|c_ms=1; _alizs_cate_info_=1042954%252C10283; _alizs_area_info_=1001; _alizs_user_type_=purchaser; _alizs_base_attr_type_=0; UM_distinctid=174be80a5e84ad-06b4951bc00d73-333769-e1000-174be80a5e930c; taklid=9600be61a686479cb01cb49f15bd9cfa; cookie2=167e49f0bd5118e188156d5057cfec8e; t=2e09211d408c4672133f88cd3b7a57c1; _tb_token_=fe9e3f87be7eb; _csrf_token=1601004375615; xlly_s=1; CNZZDATA1253659577=799699797-1600920338-https%253A%252F%252Fs.1688.com%252F%7C1601012153; CNZZDATA1261052687=316766957-1600922358-https%253A%252F%252Fdetail.1688.com%252F%7C1601008873; cbu_mmid=7E3C55520E991B9B12A5E5827CFF97F0058A8D1DB69B81595CF1BF53E412F62509F848C1F03189F2DDDCA31D76FEC8452DBD4131FDA3530A18579B8D0BCF7878; cookie1=BxNSonczp%2BfH4JvkmZGiHVjnsgV7tsFybnrAAaVXt9g%3D; cookie17=UU6m3oSoOMkDcQ%3D%3D; sg=437; csg=229583fc; unb=2671514723; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSdoC3JDBP2R&nk4=0%400AdtZS03tnds0llDWCRcSihqN1j2LxKsh6Ub; __cn_logon__=true; __cn_logon_id__=%E6%96%8C%E7%88%B7%E7%88%B71058169464; ali_apache_tracktmp=c_w_signed=Y; _nk_=%5Cu658C%5Cu7237%5Cu72371058169464; last_mid=b2b-26715147234e376; _is_show_loginId_change_block_=b2b-26715147234e376_false; _show_force_unbind_div_=b2b-26715147234e376_false; _show_sys_unbind_div_=b2b-26715147234e376_false; _show_user_unbind_div_=b2b-26715147234e376_false; __rn_alert__=false; ad_prefer="2020/09/25 14:08:51"; alicnweb=touch_tb_at%3D1601014982339%7Clastlogonid%3D%25E6%2596%258C%25E7%2588%25B7%25E7%2588%25B71058169464; ta_info=69D091960A00D3F2363D55CAD75990D7AF2651492692FC72F8FCD304CF11CF6EB039D1B914DC75A32392DE49999E6CF514A5CAB8BECF8977DE7968DE794B3E5DE4D80749A848EECD4A564C51A6AD590042C2F8C1A44CADB9BB1DEE3769A06B57BD4E9C6D546A8C0DCAD7F28B7452A04D4597474615EEC31F8A0CFB78BA1469E57C83E744E0A5247817435F95BB7F7A6F157176A5EBB663E5B39B3BF273B409F40D65725580AF691F33DF35E41471D7A2; JSESSIONID=4172B7E9F8F88C1B1F2C734A6A1C9AFE; l=eBal7oplOYd8rLtCBOfZlurza77TAIRf_uPzaNbMiOCPOqBwuj0dWZrBDO-eCnGVnsgHR3RSn5QMBWTgJyUIhlUhzn9TULS3OdTh.; isg=BDg4QMo-k_Yj4v9cdrC4_7fXCebKoZwrRtNXN3Kpr3M_jdl3GrJeu9TvQYU92lQD; tfstk=cqrGB64JdPu_kU33PGi_FngJeTtGZffZ_orTYkY9XiKsK-EFi_Lez5vdKXPgDE1..'

        self.data_url = 'https://search.1688.com/service/marketOfferResultViewService?keywords=%s&n=y&netType=1,11,16&beginPage=%s&async=true&asyncCount=20&pageSize=60&requestId=1231171737101601014130780000553&startIndex=%s'
        self.end_page = 50
        super(S1688Spider, self).__init__(*args, **kwargs)
        self.browser.get('https://www.1688.com/')
        cookies = self.stringToDict()
        self.logger.debug(cookies)
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
            itemDict['domain'] = '.1688.com'
            itemDict['expires'] = None
            cookies.append(itemDict)
        return cookies

    def start_requests(self):
        for i in range(self.page, self.end_page):
            for j in [0, 20, 40]:
                yield scrapy.Request(self.data_url % ('%C0%AD%B8%CB%CF%E4', i, j),callback=self.parse_list)


    def parse_list(self, response):
        data = json.loads(response.text)
        for i in data['data']['data']['offerList']:
            yield scrapy.Request(i['information']['detailUrl'], callback=self.parse_detail,meta={'usedSelenium': True})

    def parse_detail(self, response):
        item = ProduceItem()
        b_img_urls = response.xpath('//ul[@class="list-leading"]//img/@src').extract()
        a_img_urls = response.xpath('//ul[@class="nav nav-tabs fd-clr"]//img/@src').extract()
        img_urls = []
        for i in range(len(a_img_urls)):
            if a_img_urls[i].endswith('jpg'):
                a_img_urls[i] = a_img_urls[i].replace('.60x60','')
                img_urls.append(a_img_urls[i])
        for i in range(len(b_img_urls)):
            b_img_urls[i] = b_img_urls[i].replace('.32x32','')
            if b_img_urls[i].endswith('jpg'):
                img_urls.append(b_img_urls[i])
        item['tag'] = self.key_words
        item['img_urls'] = img_urls
        item['channel'] = 's1688'
        yield item
