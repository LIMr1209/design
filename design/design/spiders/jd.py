# 京东电商
import scrapy
from selenium import webdriver
import time
from design.items import ProductItem
import os
import requests
import random
from urllib.parse import unquote
import re

class JdSpider(scrapy.spiders.Spider):
    name = "jd"
    allowed_domains = ["search.jd.com"]
    start_urls = [
        "https://search.jd.com"
    ]
    cookies = {"__jdu":"1504540579","xtest":"8417.cf6b6759","shshshfpa":"809881f3-e0b7-a978-e43d-c273ef43feba-1547618014","shshshfpb":"a1YprPpOwUxdo4mm8gl4Z6Q%3D%3D","qrsc":"3","user-key":"b66a81b7-5bf0-46c0-978a-9a720bd8cecc","cn":"0","mt_xid":"V2_52007VwMWU1hcV1sbTxFsBWFWEgINXltGSk4QDBliA0cCQVFbWBtVTl9QYwQaUQ0MW10deRpdBW8fE1FBWFdLH0gSXwdsABFiX2hSah1NHVUBZgsXV21YV1wY","_gcl_au":"1.1.1305404444.1550111031","unpl":"V2_ZzNtbUtfQUJxAU4EK0kPDGJWQF4RAkMVc19AAHweVQA3BkJeclRCFX0UR1dnGVUUZwYZWUNcQBJFCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHsdXQBjBhNZRF9zJXI4dmR%2fH1QAbwoiXHJWc1chVE5dehFfSGcHE1hGUkIRcwB2VUsa","CCC_SE":"ADC_zaPEmyTs5ShlPGdnwf49YCNXcSLezlrSejtd8ZkWINX4xFev5mLDKQDK6wpOnjdUMU8f4tUIWS772Sq7IXjmV15Gq8UmoKdAMSCxqa%2bchyKKWP7B1wn4FZkM7y4uOt9nZ%2fm1NgPJeEBlkUpzbSkX7rqbN4qzCX%2fqCxBga4qeMvbQGIY%2f048Phg9TDCkynfkfo1IR4Tlb2DjQQPWBsvVH1bkkeOLM81OiGp4RFHKCLRVUfj%2bfxJ9%2fqjpRYlPlf58wBkrcewAYPFUMWQGSsraN2qVmJ9BiOXYNtgsbpQriVUUeBzlSeh0iIID4o4J81d10d5KsLxhqLOwS1rIpB0FxepzBSUg2od9xVP8cX0coiynwZgr5pnTwgmHJS2nwwieexheCkH3pUr1Mj6ypYi3N6uCfD9Ketn09EUNSuumFGerAXPQXnQa86Vwhqkx1bTMx1yz%2biL7kBkrLbcStHpT3IXyplcprKvxeUPVOxVgnoiCSYAxAmtcvk95XA0gWZdXoUTbfuqsNdihIag%2f823y7PU1xGMXJcvjAoEhvABoi9tntdRqo0YLI7CmrW2pVJxPfQSTMDjebrlaN5jrJvm8bnRAo7oTuJES4xMC2Vvc1i1XdkqJuoLnVvY%2fyykoOns1E2D3QzKEyz0cJyfB0oj%2f7UmLCZ9u0DJRux%2fvaUWhFhWt3piHscCzUUMlaouiSqfbYIWtHSz938m6zGnjUJYV31e1m%2fQ8fxQ711AmmLSWH9Xw%3d","__jda":"122270672.1504540579.1547547744.1550472608.1550472643.16","__jdc":"122270672","__jdv":"122270672|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_893f589aaab84dc2bd117f7e6684a4a2|1550472642940","ipLoc-djd":"53283-53309-0-0","rkv":"V0500","shshshfp":"54799f70e6b1c62917854d5ef6c209ed","3AB9D23F7A4B3C9B":"4VNI4Z2IPWV5NDI3RK77JJJZ53DLOSPHC4FSLCLXHRH5WCL7NNCFXQIDPKSN2EB6ZWZ7VQUTVPQTIXGD2TXMSDXRL4","__jdb":"122270672.7.1504540579|16.1550472643","shshshsID":"1538781fbcd6daa2ca4759c596f01eb9_5_1550473754874"}
    key_words = "热水器"
    
    def start_requests(self):
        browser = webdriver.Chrome()
        for i in range(1,8):
            browser.get("https://search.jd.com/Search?keyword=%s&wq=%s&page=%d&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&stock=1&s=61&click=0" %(self.key_words, self.key_words ,i))
            urls = browser.find_elements_by_xpath('//div[@class="p-img"]/a[@target="_blank"]')
            for url in urls:
                yield scrapy.Request(url.get_attribute('href'), callback=self.parse)
            # break

    def parse(self, response):
        print('*' * 10)
        # item = ProductItem()
        # item['url'] = response.url
        # item['title'] = response.xpath('//div[@class="sku-name"]/text()').extract()[0].strip().replace('/n','')
        # item['evt'] = 7
        # item['channel'] = 'jd_search'
        tmp_urls = response.xpath('//div[@id="spec-list"]/ul/li/img/@data-url').extract()
        img_urls = []
        for tmp_url in tmp_urls:
            img_urls.append("http://img10.360buyimg.com/n0/%s" % tmp_url)
        # item['img_urls'] = ','.join(img_urls)
        ################################保存图片 start
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
        ################################保存图片 end

        # tags = response.xpath('//div[@id="crumb-wrap"]/descendant::a[@clstag]/text()').extract()[0:3]
        # item['tags'] = ','.join(tags)
        # item['brand_tags'] = response.xpath('//ul[@id="parameter-brand"]/li/a/text()').extract()[0]
        #
        # price = response.xpath('//div[@class="dd"]/span[@class="p-price"]/span[2]/text()').extract()
        # if price is not None:
        #     try :
        #         item['price'] = price[0]
        #         item['currency_type'] = 1
        #     except IndexError:
        #         pass
        # print(item)
        # yield item
        