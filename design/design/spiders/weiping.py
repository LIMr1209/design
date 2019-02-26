# 唯品会
import scrapy
from selenium import webdriver
import time
import os
import requests
import random

from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.spiders.Spider):
    name = "weiping"
    key_words = "路由器"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    def start_requests(self):
        browser = webdriver.Chrome(options=self.chrome_options)
        for i in range(1, 3):
            browser.get(
                "https://category.vip.com/suggest.php?keyword=%s&page=%s" % (
                    self.key_words, i))
            urls = browser.find_elements_by_xpath('//div[@class="goods-image"]/a')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)

    def parse(self, response):
        print('*' * 10)
        img_urls = response.xpath('//div[@id="J-sImg-wrap"]/div[position()>1]/img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('64x64', '420x420')
            if not img_urls[i].startswith('https'):
                img_urls[i] = 'https://' + img_urls[i]
        print(img_urls)
        # for img_url in img_urls:
        #     try:
        #         path = './image_test/' + self.key_words
        #         isExists = os.path.exists(path)
        #         if not isExists:
        #             os.makedirs(path)
        #         img_response = requests.get(img_url, timeout=5)
        #         a = int(time.time())
        #         b = random.randint(10, 100)
        #         num = str(a) + str(b)
        #         try:
        #             with open(path + '/' + num + '.jpg', 'wb') as file:
        #                 file.write(img_response.content)
        #                 print('保存成功')
        #         except:
        #             print('保存图片失败')
        #     except:
        #         print('访问图片失败')
