# 亚马逊
import scrapy
import os
import requests
import time
import random
from design.settings import USER_AGENTS


class AmazonSpider(scrapy.spiders.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    key_word = "打印机"
    cookie = {"x-wl-uid": "1HLv1HxJzEtQLlBYWMfv7puk8/voXH/VIgoiQ9ewAWWntrB+0QJz17S/Yi9k9IVEHfJxncjXErfE=",
              "session-id": "459-1170388-1651454", "ubid-acbcn": "459-7032326-5051849",
              "session-token": "'ZJr/OPdrRIP7Tg8VLRvOkiU68zMtoU5eJ0VNVhwpkZYpwsoOp78gmf78w3me5drvIPjhR0vKW21oGo/SttpKHZ9YWIIowhPkk9y5Wx2wDOvLg8wjCtSfM9v4jikU1g7/9w2Gsl+nrPvTdOMsvUY2cxJ8HEdA50qFVn/3xpxquzX5nd4NU3qu+9ekVv9N8pyRcDojYHFKEuGkrKRRYrTRclwT/G1lMsJ8ESuXsXGfumdB758Mm1RNfA=='",
              "i18n-prefs": "CNY", "session-id-time": "2082787201l",
              "csm-hit": "tb:11Z75V7KVZRH53JGJTV8+sa-11Z75V7KVZRH53JGJTV8-9TCZAX86FDRJFQG2VEK4|1550628429630&t:1550628429630&adb:adblk_no"}

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
        img_urls = response.xpath('//a[@class="a-link-normal a-text-normal"]/img/@src').extract()

        ################################保存图片 start
        for img_url in img_urls:
            img_url = img_url.replace('AA200', 'SX679')
            try:
                path = './image_test/' + self.key_word
                isExists = os.path.exists(path)
                if not isExists:
                    os.makedirs(path)
                img_response = requests.get(img_url, timeout=5)
                a = int(time.time())
                b = random.randint(10, 100)
                num = str(a) + str(b)
                try:
                    with open(path + '/' + num + '.jpg', 'wb') as file:
                        file.write(img_response.content)
                        print('保存成功')
                except:
                    print('保存图片失败')
            except:
                print('访问图片失败')
