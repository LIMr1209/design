import re

import scrapy
from pydispatch import dispatcher
from scrapy import signals

from design.items import DesignItem
# scrapy 信号相关库
from design.spiders.selenium import SeleniumSpider
import datetime

data = {
    'channel': 'yankodesign',
    'evt': 3,
}


class DesignCaseSpider(SeleniumSpider):
    name = 'yankodesign'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.yankodesign.com']
    date_threshold = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y/%m/%d')
    category_list = ['productdesign', 'technology', 'automotive']
    category_id = 0
    fail_url = []
    url = 'http://www.yankodesign.com/category/%s/page/%s'

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.UserAgentSpiderMiddleware': 400,
            'design.middlewares.SeleniumMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    def __init__(self, *args, **kwargs):

        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        super(DesignCaseSpider, self).__init__(*args, **kwargs)

    def except_close(self):
        print(self.fail_url)

    def start_requests(self):
        # fail_url = []
        # for i in fail_url:
        #     yield scrapy.Request(i, callback=self.parse_detail)
        yield scrapy.Request(self.url % (self.category_list[self.category_id], 1),
                             meta={'page': 1},
                             callback=self.parse_list)

    def parse_list(self, response):
        page = response.meta['page']
        detail_list = response.xpath('//article/figure/a/@href').extract()
        if not detail_list:
            print(self.category_id, page)
        # yield scrapy.Request(detail_list[0], callback=self.parse_detail, meta={'usedSelenium': True})
        continue_count = 0
        date_re = re.compile(r'\d+/\d+/\d+')
        for i in detail_list:
            if match := date_re.search(i):
                if match.group() < self.date_threshold:
                    continue_count += 1
                    continue
            yield scrapy.Request(i, callback=self.parse_detail)
        # max_page = response.xpath('//a[@class="page-numbers"][last()]/text()').extract()[0].replace(',', '')
        # if page < int(max_page) and continue_count < len(detail_list):
        if continue_count < len(detail_list):
            page += 1
            yield scrapy.Request(url=self.url % (self.category_list[self.category_id], page), callback=self.parse_list,
                                 meta={'page': page})
        else:
            self.category_id += 1
            if len(self.category_list) == self.category_id:
                return
            yield scrapy.Request(url=self.url % (self.category_list[self.category_id], 1), callback=self.parse_list,
                                 meta={'page': 1})

    #
    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        try:
            try:
                res = response.xpath('//div[@class="single-box clearfix entry-content"]').extract()[0]
            except:
                res = response.xpath('//div[@class="single-box clearfix entry-content jpibfi_container"]').extract()[0]
            img_text = str(res)
            rex = re.compile('<noscript><img.*?src="(.*?)".*?</noscript>')
            img_urls = rex.findall(img_text)
            for i in range(len(img_urls)):
                # if not img_urls[i].startswith('https://www.yankodesign.com'):
                #     img_urls[i] = 'https://www.yankodesign.com' + img_urls[i]
                img_urls[i] = img_urls[i].replace("amp;", '').replace("#038;", "")
            if not img_urls:
                try:
                    img_urls = response.xpath(
                        '//img[contains(@class,"alignnone size-full") or contains(@class, "aligncenter size-full")]/@src').extract()
                except:
                    img_urls = response.xpath('//img[@class="postpic"]/@src').extract()
            designer = " ".join(
                response.xpath(
                    '//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designer:")]//text()').extract()).strip()[
                       9:]

            if not designer:
                designer = " ".join(
                    response.xpath(
                        '//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designers:")]//text()').extract()).strip()[
                           10:]

            title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
            desc_list_p = response.xpath('//div[@class="grid-8 column-1"]/div[1]/p')
            desc_text_list = []
            for i in desc_list_p:
                desc = i.xpath('string(.)').extract()[0]
                if desc:
                    b = re.search("Designer[s]*:[\s\S]*", desc)
                    if b:
                        continue
                    desc_text_list.append(desc)
            remark = '\n'.join(desc_text_list)
            tags = ','.join(response.xpath('//div[@class="single-box tag-box clearfix"]/a/text()').extract())
            item['url'] = url
            if tags:
                item['tags'] = tags
            item['img_urls'] = ','.join(img_urls)
            if designer:
                item['designer'] = designer.strip()
            item['title'] = title.strip()
            if remark:
                item['description'] = remark
            for key, value in data.items():
                item[key] = value
        except:
            self.fail_url.append(url)
        yield item
