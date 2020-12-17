# Gadget Flow

import scrapy
import json
from design.items import DesignItem
import time
import os
import requests

class GadgetSpider(scrapy.spiders.Spider):
    name = "gadget"
    allowed_domains = ["thegadgetflow.com"]

    def start_requests(self):
        # url = "https://thegadgetflow.com/gfl-infinite/%d/_/_/_/_/ar/_/_/_/guest/"
        url = "https://thegadgetflow.com/gfl-infinite/%d/_/_/_/_/ar/_/_/_/guest/"
        for page in range(1,1000,6):
            time.sleep(0.2)
            yield scrapy.Request(url % (page), callback=self.body_response)

    def body_response(self, response):
        urls = response.xpath('//a[@class="gfl-thumb-link"]/@href').extract()
        for url in urls:
            time.sleep(0.3)
            yield scrapy.Request(url, callback=self.item_page)
	
    def item_page(self, response):
        # img_urls = response.xpath('//meta[@property="og:image"]/@content').extract()
        # img_url = img_urls[0]
        # print(img_url)
        # try:
        #     path = './gadget_image/'
        #     isExists = os.path.exists(path)
        #     if not isExists:
        #         os.makedirs(path)
        #     # chrome_options = Options()
        #     # chrome_options.add_argument("--headless")
        #     # browser = webdriver.Chrome(chrome_options=chrome_options)
        #     # browser.get(img_url)
        #     img_response = requests.get(img_url, timeout=5)
        #     print(img_response.status_code)
        #     name = img_url.split('/')[-1]
        #     try:
        #         with open(path + '/' + name, 'wb') as file:
        #             file.write(img_response.content)
        #             print('保存成功')
        #     except:
        #         print('保存图片失败')
        # except:
        #     print('访问图片失败')
        item = DesignItem()
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="gfl-single"]/div[@class="gfl-single-left"]/h1/text()').extract()[0]
        item['evt'] = 7
        item['channel'] = 'gadget'
        price = response.xpath('//div[@class="gfl-single-actions"]/descendant::div[@class="gfl-button"]/descendant::span[@class="gfl-single-product-price"]/span[@itemprop="price"]/text()').extract()
        if price is not None:
            try :
                item['price'] = price[0]
                item['currency_type'] = 2
            except IndexError:
                pass
        img_urls = response.xpath('//meta[@property="og:image"]/@content').extract()
        item['img_urls'] = ','.join(img_urls)
        tmp_arr = response.xpath('//div[@class="gfl-specs-item"]/div[@class="gfl-specs-item-label"]/text()').extract()
        i = 1
        for tmp_str in tmp_arr:
            if tmp_str[0:10] == 'Categories':
                tags = response.xpath('//div[@class="gfl-specs-item"][%d]/div[@class="gfl-specs-item-content"]/a/text()' % i).extract()
                item['tags'] = ','.join(tags)
            elif tmp_str[0:8] == 'Material' :
                material = response.xpath('//div[@class="gfl-specs-item"][%d]/div[@class="gfl-specs-item-content"]/text()' % i).extract()
                item['material_tags'] = ','.join(material)
            i += 1
        # print(img_urls)
        # print('*' * 100)
        # print(item)
        yield item



