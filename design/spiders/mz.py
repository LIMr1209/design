import scrapy
import requests
import random
from fake_useragent import UserAgent


class MzSpider(scrapy.spiders.Spider):
    name = "mz"
    custom_settings = {
        'DOWNLOAD_DELAY': random.uniform(0.2, 3),
        'DOWNLOADER_MIDDLEWARES': None
    }
    page = 1
    url = 'https://www.mzitu.com/page/%s/'

    def start_requests(self):
        headers = {
            'referer': 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=https%3A%2F%2Fwww.mzitu.com%2F&fenlei=256&oq=%25E5%25A6%25B9%25E5%25AD%2590%25E5%259B%25BE&rsv_pq=a603886d000038bc&rsv_t=bda9iduSaOD3kiTdexGKHo8sNiO7We5B8evovkS8X1XxIxyWe8LdheP%2BmVw&rqlang=cn&rsv_enter=1&rsv_dl=tb&rsv_btype=i&inputT=3325&rsv_sug3=14&rsv_sug1=13&rsv_sug7=000&rsv_n=2&bs=%E5%A6%B9%E5%AD%90%E5%9B%BE',
        }
        yield scrapy.Request(url='https://www.mzitu.com/', callback=self.pages, headers=headers)


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
            yield scrapy.Request(url=self.url % self.page, callback=self.pages)

    def item_page(self, response):

        save_image_help(response)
        pages = response.xpath(
            "//div[@class='main']/div[@class='content']/div[@class='pagenavi']/a/span/text()").extract()
        end_page = pages[-2]
        for page in range(2, int(end_page)):
            headers = {
                'referer': response.url,
            }
            yield scrapy.Request(url=response.url + ('/%d/' % page), callback=self.save_img, headers=headers)

    def save_img(self, response):
        print(self.page)
        save_image_help(response)


def save_image_help(response):
    img_url = \
        response.xpath(
            "//div[@class='main']/div[@class='content']/div[@class='main-image']/p/a/img/@src").extract()[0]
    try:
        path = './image_test/mz/'
        user_agent = UserAgent().random
        headers = {
            'Referer': response.url,
            'User-Agent': user_agent
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
