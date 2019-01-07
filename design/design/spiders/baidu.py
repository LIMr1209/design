import scrapy, json
from scrapy.http import Request
from scrapy.http import FormRequest
from design.items import BaiduPicItem


class BaiduImagesSpider(scrapy.Spider):
    name = 'baidu_images'
    allowed_domains = ['http:image.baidu.com']
    start_urls = ['http://image.baidu.com/']
    key_words = '数学批改'
    base_url = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&' \
               'is=&fp=result&queryWord={0}&cl=2&lm =-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=&hd=&latest=&copyright=' \
               '&word={0}&s=&se=&tab=&width=&height=&face=0&' \
               'istype=2&qc=&nc=1&fr=&expermode=&force=&' \
               'pn={1}&rn=30&gsm=1e&'
    page = 30
    flag = True
    def parse(self, response):
        url = self.base_url.format(self.key_words, str(self.page))
        yield Request(url, callback=self.get_pic, dont_filter=True)

        if self.flag:
            self.page += 30
            yield Request('http://image.baidu.com/', callback=self.parse, dont_filter=True)

    def get_pic(self, response):
        print(self.page)
        item = BaiduPicItem()
        response_json = response.text
        response_dict = json.loads(response_json)
        response_data = response_dict['data']
        if len(response_data) == 0:
            self.flag = False
        for data in response_data:
            item['search_word'] = self.key_words
            # item['img_name'] = data['fromPageTitleEnc']  # 有的data 没有fromPageTitleEnc
            # item['img_url'] = data['middleURL']
            print(item)
            # yield item

