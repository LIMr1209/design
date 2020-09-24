# google
import scrapy
import re
from design.items import ProduceItem
from urllib.parse import unquote


class GoogleRobotImagesSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['google.com']
    key_words = [
        '冰箱'
    ]
    cookies = {"CGIC": "IgMqLyo",
               "NID": "160=LM3qWskIf9T2o_5zEtBGsD-VbciT49WCs_6SsHJO8CkwWI1AuH9qKNFvfbRtivGailN5Axnl4uI6_EPuyLQsue_JnLlEsF6tgp7Vp1sWvu7GL_WuKo9aet9FPrtxXtKKVdsyz-I3IT2AnsYwQuuKG1GtQHnzkJ0rqvXVx3I_bLo",
               "1P_JAR": "2019-02-15-02"}
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 301,
        }
    }
    base_url = 'https://www.google.com/search?q=%s&ijn=%d&start=%d&ei=pW1mXJTKIYmR8wWS4JiYCA&yv=3&tbm=isch&vet=10ahUKEwjUsM30nr3gAhWJyLwKHRIwBoMQuT0INSgB.pW1mXJTKIYmR8wWS4JiYCA.i&ved=0ahUKEwjUsM30nr3gAhWJyLwKHRIwBoMQuT0INSgB&asearch=ichunk&async=_id:rg_s,_pms:s,_fmt:pc'

    def start_requests(self):
        for key_word in self.key_words:
            for count in range(100, 1500, 100):
                page = int(count / 100)
                headers = {'referer': 'https://www.google.com/',
                           'x-client-data': 'CIm2yQEIorbJAQjBtskBCKmdygEIqKPKAQi/p8oBCOSoygEY+aXKAQ=='}
                yield scrapy.Request(url=self.base_url % (key_word, page, count), callback=self.parse, dont_filter=True,
                                     headers=headers, cookies=self.cookies, meta={'key_word': key_word})

    def parse(self, response):
        item = ProduceItem()
        img_urls = re.findall('imgurl=(http.*?)&', response.text)
        page = unquote(re.findall('ijn=(.*?)&', response.url)[0], 'utf-8')
        print('第' + page + '页')
        item['tag'] = response.meta['key_word']
        item['img_urls'] = img_urls
        item['channel'] = 'google'
        yield item
