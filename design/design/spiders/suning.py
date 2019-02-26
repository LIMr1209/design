# 苏宁
import scrapy
import time
import os
import requests
import random


class SNSpider(scrapy.spiders.Spider):
    name = "suning"
    key_words = "路由器"
    cp = 0
    paging = 0
    url = 'https://search.suning.com/emall/searchV1Product.do?keyword=%s&ci=157162&pg=01&cp=%s&il=0&st=0&iy=0&isDoufu=1&isNoResult=0&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=010&paging=%s&sub=0&jzq=3124'
    start_urls = [url % (key_words, cp, paging)]

    def parse(self, response):
        detail_urls = response.xpath('//li//div[@class="title-selling-point"]/a/@href').extract()
        for i in range(len(detail_urls)):
            if not detail_urls[i].startswith('https'):
                detail_urls[i] = 'https:' + detail_urls[i]
        for url in detail_urls:
            yield scrapy.Request(url, callback=self.parse_detail, )
        if self.paging < 3:
            self.paging += 1
            yield scrapy.Request(self.url % (self.key_words, self.cp, self.paging))
        else:
            if self.cp < 2:
                self.paging = 0
                self.cp += 1
                yield scrapy.Request(self.url % (self.key_words, self.cp, self.paging))

    def parse_detail(self, response):
        image_urls = response.xpath('//div[@class="imgzoom-thumb-main"]//img/@src').extract()
        for i in range(len(image_urls)):
            image_urls[i] = image_urls[i].replace('60w_60h', '800w_800h')
            if not image_urls[i].startswith('http'):
                image_urls[i] = 'http:' + image_urls[i]
        for img_url in image_urls:
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
