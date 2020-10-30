import re

import scrapy
from design.items import DesignItem
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
# scrapy 信号相关库
from scrapy import signals
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher
from .selenium import SeleniumSpider

data = {
    'channel': 'yankodesign',
    'evt': 3,
}


class DesignCaseSpider(SeleniumSpider):
    name = 'yankodesign'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.yankodesign.com']
    page = 1

    # category_list = ['productdesign']
    # category_list = [ 'technology']
    # category_list = ['automotive']
    # category_list = ['architecture']
    category_list = ['productdesign', 'technology', 'automotive', 'architecture', 'deals', 'sustainable-design']
    category_id = 1
    url = 'http://www.yankodesign.com/category/' + category_list[category_id] + '/'
    # start_urls = [url+'page/'+str(page)]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.SeleniumMiddleware': 543,
        },
        'ITEM_PIPELINES' : {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    # 将chrome初始化放到spider中，成为spider中的元素

    def start_requests(self):
        yield scrapy.Request(self.url + 'page/' + str(self.page), meta={'usedSelenium': True})

    def parse(self, response):
        detail_list = response.xpath('//article/figure/a/@href').extract()
        try:
            tags = response.xpath('//div[@class="title-with-sep page-title"]/h1/text()').extract()[0]
        except:
            tags = response.xpath('//div[@class="wrapper"]/h1/text()').extract()[0]
        yield scrapy.Request(detail_list[0], callback=self.parse_detail, meta={'tags': tags, 'usedSelenium': True})
        # for i in detail_list:
        #     yield scrapy.Request(i, callback=self.parse_detail, meta={'tags': tags, 'usedSelenium': True})
        # page = response.xpath('//a[@class="page-numbers"][last()]/text()').extract()[0].replace(',', '')
        # print(tags, "总页数", page)
        # if self.page < int(page):
        #     self.page += 1
        #     print(tags, "   ", self.page)
        #     yield scrapy.Request(url=self.url + 'page/' + str(self.page), callback=self.parse,
        #                          meta={'usedSelenium': True})
        # else:
        #     self.page = 1
        #     self.category_id += 1
        #     yield scrapy.Request(self.url, callback=self.parse, meta={'usedSelenium': True})

    def parse_detail(self, response):
        tags = response.meta['tags']
        item = DesignItem()
        url = response.url
        print('分类', tags, '页数', self.page)
        # try:
        #     img_urls = response.xpath('//img[contains(@class,"alignnone size-full")]/@src').extract()
        # except:
        #     img_urls = response.xpath('//img[@class="postpic"]/@src').extract()
        res = response.xpath('//div[@class="single-box clearfix entry-content"]').extract()[0]
        img_text = str(res)
        rex = re.compile('<noscript>&lt;img.*?src="(.*?)".*?</noscript>')
        img_urls = rex.findall(img_text)
        if not img_urls:
            a = 1
        for i in range(len(img_urls)):
            # if not img_urls[i].startswith('https://www.yankodesign.com'):
            #     img_urls[i] = 'https://www.yankodesign.com' + img_urls[i]
            img_urls[i] = img_urls[i].replace("amp;",'').replace("#038;","")
        designer = " ".join(
            response.xpath('//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designer")]//text()').extract())[10:]
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
        try:
            remark = response.xpath('//div[@class="grid-8 column-1"]/div[1]/p[position()<4][2]/text()').extract()[0]
        except:
            try:
                remark = response.xpath('//div[@class="wrapper"]/div[1]/p[1]/text()').extract()[0]
            except:
                remark = ''
        if len(remark) > 480:
            remark = remark[:480]
        tags = ','.join(response.xpath('//div[@class="single-box tag-box clearfix"]/a/text()').extract())
        item['url'] = url
        item['tags'] = tags
        item['img_urls'] = ','.join(img_urls)
        item['designer'] = designer.strip()
        item['title'] = title.strip()
        item['sub_title'] = ''
        item['description'] = remark.replace('\n', '').replace('\n\r', '').strip()
        item['info'] = ''
        print(item)
        for key, value in data.items():
            item[key] = value
        yield item

# class Random(scrapy.Spider):
#     name = 'yankodesign'
#     handle_httpstatus_list = [404]
#     allowed_domains = ['www.yankodesign.com']
#     start_urls = ['http://www.yankodesign.com/random-designs/']
#
#     def parse_list(self, response):
#         detail_list = response.xpath('//article/figure/a/@href').extract()
#         try:
#             tags = response.xpath('//div[@class="title-with-sep page-title"]/h1/text()').extract()[0]
#         except:
#             tags = response.xpath('//div[@class="wrapper"]/h1/text()').extract()[0]
#         for i in detail_list:
#             yield scrapy.Request(i, callback=self.parse_detail, meta={'tags': tags})
#         for i in range(200):
#             yield scrapy.Request('http://www.yankodesign.com/random-designs/',callback=self.parse_list)
#     def parse_detail(self, response):
#         tags = response.meta['tags']
#         item = DesignItem()
#         url = response.url
#         print('分类', tags)
#         img_url = response.xpath('//img[contains(@class,"alignnone size-full")]/@src').extract()[0]
#         designer = " ".join(response.xpath('//p[contains(text(),"Designer")]//text()').extract())[10:]
#         title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
#         remark = response.xpath('//div[@class="grid-8 column-1"]/div[1]/p[position()<4][2]/text()').extract()[0]
#         if len(remark) > 480:
#             remark = remark[:480]
#         print("设计师", designer)
#         print('图片地址', img_url)
#         print('标题',title)
#         print('备注',remark)
#         print('*'*50)
#         item['url'] = url
#         item['tags'] = tags
#         item['img_url'] = img_url
#         item['designer'] = designer.strip()
#         item['title'] = title.strip()
#         item['remark'] = remark.replace('\n', '').replace('\n\r', '').strip()
#         for key, value in data.items():
#             item[key] = value
#         yield item
