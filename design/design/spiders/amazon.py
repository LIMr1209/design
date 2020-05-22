# 亚马逊
import scrapy
import time
import random
from design.settings import USER_AGENTS
from design.items import ProduceItem


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    key_word = '胎心仪'
    cookie = {"x-wl-uid": "1HLv1HxJzEtQLlBYWMfv7puk8/voXH/VIgoiQ9ewAWWntrB+0QJz17S/Yi9k9IVEHfJxncjXErfE=",
              "session-id": "459-1170388-1651454", "ubid-acbcn": "459-7032326-5051849",
              "session-token": "'ZJr/OPdrRIP7Tg8VLRvOkiU68zMtoU5eJ0VNVhwpkZYpwsoOp78gmf78w3me5drvIPjhR0vKW21oGo/SttpKHZ9YWIIowhPkk9y5Wx2wDOvLg8wjCtSfM9v4jikU1g7/9w2Gsl+nrPvTdOMsvUY2cxJ8HEdA50qFVn/3xpxquzX5nd4NU3qu+9ekVv9N8pyRcDojYHFKEuGkrKRRYrTRclwT/G1lMsJ8ESuXsXGfumdB758Mm1RNfA=='",
              "i18n-prefs": "CNY", "session-id-time": "2082787201l",
              "csm-hit": "tb:11Z75V7KVZRH53JGJTV8+sa-11Z75V7KVZRH53JGJTV8-9TCZAX86FDRJFQG2VEK4|1550628429630&t:1550628429630&adb:adblk_no"}

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImageSavePipeline': 300
        },
    }

    def start_requests(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "user-agent": random.choice(USER_AGENTS)
        }
        url = "https://www.amazon.cn/s/ref=sr_pg_%d?rh=i:aps,k:%s&page=%d&keywords=%s&ie=UTF8&qid=%d"
        for page in range(1, 21):
            t = int(time.time())
            yield scrapy.Request(url=url % (page, self.key_word, page, self.key_word, t), callback=self.list_page,
                                 cookies=self.cookie, headers=headers)

    def list_page(self, response):
        item = ProduceItem()
        img_urls = response.xpath('//a[@class="a-link-normal a-text-normal"]/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('AA200', 'SX679')
        item['tag'] = self.key_word
        item['img_urls'] = img_urls
        yield item
