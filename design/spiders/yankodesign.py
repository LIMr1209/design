import re

import scrapy
from design.items import DesignItem
# scrapy 信号相关库
from .selenium import SeleniumSpider

data = {
    'channel': 'yankodesign',
    'evt': 3,
}


class DesignCaseSpider(SeleniumSpider):
    name = 'yankodesign'
    # handle_httpstatus_list = [404]
    allowed_domains = ['www.yankodesign.com']
    page = 33

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
        'DOWNLOAD_DELAY': 2,
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
        # yield scrapy.Request("https://www.yankodesign.com/2019/08/21/garmin-needs-a-senior-industrial-designer/", meta={'usedSelenium': True}, callback=self.parse_detail)
        yield scrapy.Request(self.url + 'page/' + str(self.page), meta={'usedSelenium': True})

    def parse(self, response):
        detail_list = response.xpath('//article/figure/a/@href').extract()
        # try:
        #     tags = response.xpath('//div[@class="title-with-sep page-title"]/h1/text()').extract()[0]
        # except:
        #     tags = response.xpath('//div[@class="wrapper"]/h1/text()').extract()[0]
        # yield scrapy.Request(detail_list[0], callback=self.parse_detail, meta={'usedSelenium': True})
        for i in detail_list:
            yield scrapy.Request(i, callback=self.parse_detail, meta={'usedSelenium': True})
        page = response.xpath('//a[@class="page-numbers"][last()]/text()').extract()[0].replace(',', '')
        print("总页数", page)
        if self.page < 350:
        # if self.page < 1150:
        # if self.page < int(page):
            self.page += 1
            print("   ", self.page)
            yield scrapy.Request(url=self.url + 'page/' + str(self.page), callback=self.parse,
                                 meta={'usedSelenium': True})
        # else:
        #     self.page = 1
        #     self.category_id += 1
        #     yield scrapy.Request(self.url, callback=self.parse, meta={'usedSelenium': True})
    #
    def parse_detail(self, response):
        # tags = response.meta['tags']
        item = DesignItem()
        url = response.url
        print('页数', self.page)
        # try:
        #     img_urls = response.xpath('//img[contains(@class,"alignnone size-full")]/@src').extract()
        # except:
        #     img_urls = response.xpath('//img[@class="postpic"]/@src').extract()
        try:
            res = response.xpath('//div[@class="single-box clearfix entry-content"]').extract()[0]
        except:
            res = response.xpath('//div[@class="single-box clearfix entry-content jpibfi_container"]').extract()[0]
        img_text = str(res)
        rex = re.compile('<noscript>&lt;img.*?src="(.*?)".*?</noscript>')
        img_urls = rex.findall(img_text)
        for i in range(len(img_urls)):
            # if not img_urls[i].startswith('https://www.yankodesign.com'):
            #     img_urls[i] = 'https://www.yankodesign.com' + img_urls[i]
            img_urls[i] = img_urls[i].replace("amp;",'').replace("#038;","")
        designer = " ".join(
            response.xpath('//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designer:")]//text()').extract()).strip()[9:]

        if not designer:
            designer = " ".join(
                response.xpath(
                    '//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designers:")]//text()').extract()).strip()[10:]
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
        try:
            remark = "\n".join(response.xpath('//div[@class="grid-8 column-1"]/div[1]/p/text()').extract())
        except:
            remark = ""
            # try:
            #     remark = response.xpath('//div[@class="wrapper"]/div[1]/p/text()').extract()[0]
            # except:
            #     remark = ''
        tags = ','.join(response.xpath('//div[@class="single-box tag-box clearfix"]/a/text()').extract())
        b = re.search("Designer[s]*:[\s\S]*", remark)
        try:
            remark.replace(b.group(),'')
        except:
            pass
        item['url'] = url
        if tags:
            item['tags'] = tags
        item['img_urls'] = ','.join(img_urls)
        if designer:
            item['designer'] = designer.strip()
        item['title'] = title.strip()
        if remark:
            item['description'] = remark
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