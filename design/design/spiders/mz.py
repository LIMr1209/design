import scrapy
import os
import requests
import random
from design.settings import USER_AGENTS


class MzSpider(scrapy.spiders.Spider):
    name = "mz"
    custom_settings = {
        'DOWNLOAD_DELAY': random.uniform(0.2, 3),
        'DOWNLOADER_MIDDLEWARES': None
    }

    def start_requests(self):
        url = 'https://www.mzitu.com/page/%d/'
        for page in range(1, 20):
            yield scrapy.Request(url=url % (page))
            # break

    def parse(self, response):
        urls = response.xpath(
            "//div[@class='main']/div[@class='main-content']/div[@class='postlist']/ul[@id='pins']/li/a/@href").extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.item_page)
            # break

    def item_page(self, response):
        pages_one = response.xpath(
            "//div[@class='main']/div[@class='content']/div[@class='pagenavi']/a/span/text()").extract()
        title = response.xpath('//h2[@class="main-title"]/text()').extract()[0]
        end_page = pages_one[-2]
        for page in range(1, int(end_page)):
            headers = {
                'referer': page,
                "user-agent": random.choice(USER_AGENTS)
            }
            yield scrapy.Request(url=response.url + ('/%d/' % page), callback=self.save_img, headers=headers,
                                 meta={'title': title})
            # break

    def save_img(self, response):
        img_url = \
        response.xpath("//div[@class='main']/div[@class='content']/div[@class='main-image']/p/a/img/@src").extract()[0]
        print(img_url)
        title = response.meta['title'][:5]
        url = response.url
        try:
            path = './image_test/mz/' + title
            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)
            headers = {
                "user-agent": random.choice(USER_AGENTS),
                'referer': url
            }
            img_response = requests.get(img_url, timeout=5, headers=headers)
            print(img_response.status_code)
            name = img_url.split('/')[-1]
            try:
                with open(path + '/' + name, 'wb') as file:
                    file.write(img_response.content)
                    print('保存成功')
            except:
                print('保存图片失败')
        except:
            print('访问图片失败')
