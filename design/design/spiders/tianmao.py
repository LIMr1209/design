# 天猫
import scrapy
from selenium import webdriver
import time
import os
import requests
import random

from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.spiders.Spider):
    name = "tianmao"
    key_words = "路由器"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    def start_requests(self):
        browser = webdriver.Chrome(options=self.chrome_options)

        for i in range(8):
            s = i * 60
            browser.get(
                "https://list.tmall.com/search_product.htm?q=%s&s=%s&type=p&vmarket=&spm=875.7931836/B.a2227oh.d100&from=mallfp..pc_1_searchbutton" % (
                    self.key_words, s))
            urls = browser.find_elements_by_xpath('//div[@class="productImg-wrap"]/a')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)

    def parse(self, response):
        print('*' * 10)
        img_urls = response.xpath('//ul[@id="J_UlThumb"]//img/@src').extract()
        for i in range(len(img_urls)):
            img_urls[i] = img_urls[i].replace('_60x60q90.jpg', '')
            if not img_urls[i].startswith('https'):
                img_urls[i] = 'https://' + img_urls[i]
        print(img_urls)
        # for img_url in img_urls:
        #     try:
            #     path = './image_test/' + self.key_words
            #     isExists = os.path.exists(path)
            #     if not isExists:
            #         os.makedirs(path)
            #     img_response = requests.get(img_url, timeout=5)
            #     a = int(time.time())
            #     b = random.randint(10, 100)
            #     num = str(a) + str(b)
            #     try:
            #         with open(path + '/' + num + '.jpg', 'wb') as file:
            #             file.write(img_response.content)
            #             print('保存成功')
            #     except:
            #         print('保存图片失败')
            # except:
            #     print('访问图片失败')
