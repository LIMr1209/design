import scrapy
import requests
import random


class MzSpider(scrapy.spiders.Spider):
    name = "mz"
    custom_settings = {
        'DOWNLOAD_DELAY': random.uniform(0.2, 3),
        'DOWNLOADER_MIDDLEWARES': None
    }
    page = 1
    start_url = 'https://www.mzitu.com/zipai/'
    url = 'https://www.mzitu.com/page/%s/'
    start_urls = [start_url]

    def parse(self, response):
        headers = {
            'referer': response.url,
        }
        yield scrapy.Request(url='https://www.mzitu.com/', callback=self.item_page, headers=headers)

    def pages(self, response):
        urls = response.xpath(
            "//div[@class='main']/div[@class='main-content']/div[@class='postlist']/ul[@id='pins']/li/a/@href").extract()
        for url in urls:
            headers = {
                'referer': response.url,
            }
            yield scrapy.Request(url=url, callback=self.item_page, headers=headers)
        if self.page < 218:
            self.page += 1
            yield scrapy.Request(url=self.url % self.page, callback=self.item_page)

    def item_page(self, response):
        img_url = \
            response.xpath(
                "//div[@class='main']/div[@class='content']/div[@class='main-image']/p/a/img/@src").extract()[0]
        try:
            path = './image_test/mz/'
            headers = {
                'referer': response.url
            }
            img_response = requests.get(img_url, timeout=5, headers=headers)
            name = img_url.split('/')[-1]
            try:
                with open(path + name, 'wb') as file:
                    file.write(img_response.content)
                    print('保存成功')
            except:
                print('保存图片失败')
        except:
            print('访问图片失败')
        pages = response.xpath(
            "//div[@class='main']/div[@class='content']/div[@class='pagenavi']/a/span/text()").extract()
        end_page = pages[-2]
        for page in range(2, int(end_page)):
            headers = {
                'referer': response.url,
            }
            yield scrapy.Request(url=response.url + ('/%d/' % page), callback=self.save_img, headers=headers)

    def save_img(self, response):
        img_url = \
            response.xpath(
                "//div[@class='main']/div[@class='content']/div[@class='main-image']/p/a/img/@src").extract()[0]
        try:
            path = './image_test/mz/'
            headers = {
                'referer': response.url
            }
            img_response = requests.get(img_url, timeout=5, headers=headers)
            name = img_url.split('/')[-1]
            try:
                with open(path + name, 'wb') as file:
                    file.write(img_response.content)
                    print('保存成功')
            except:
                print('保存图片失败')
        except:
            print('访问图片失败')
