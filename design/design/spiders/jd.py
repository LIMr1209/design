# 京东电商
import scrapy
from selenium import webdriver
import time
import os
import requests
import random

from selenium.webdriver.chrome.options import Options


class JdSpider(scrapy.spiders.Spider):
    name = "jd"
    allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    key_words = "热水器"

    def start_requests(self):
        browser = webdriver.Chrome(options=self.chrome_options)
        for i in range(1, 8):
            browser.get(
                "https://search.jd.com/Search?keyword=%s&wq=%s&page=%d&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&stock=1&s=61&click=0" % (
                    self.key_words, self.key_words, i))
            urls = browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)

    def parse(self, response):
        print('*' * 10)
        img_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        for i in range(len(img_urls)):
            img_urls[i] = 'http://img10.360buyimg.com/n0/%s' % img_urls[i]
        # print(img_urls)
        for img_url in img_urls:
            try:
                path = './image_test/' + self.key_words
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
