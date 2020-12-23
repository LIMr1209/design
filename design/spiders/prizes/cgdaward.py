# 当代好设计奖
import copy
import scrapy
import json, requests
from design.items import DesignItem

import re




class CgdawardSpider(scrapy.spiders.Spider):
    name = "cgdaward"
    host = "https://www.cgdaward.com"
    url = "https://www.cgdaward.com/online-exhibition/index.php?search-index-mid-4-awards-%s-nianfen-%s-categories-0-guolv-0-keyword--page-%s.html"
    prize_level = {
        1: '金奖 Gold Winner',
        2: '荣誉奖 Honourable Mention',
        3: '优胜奖 Winner'
    }

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES' : {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    def start_requests(self):
        # for i in range(2015, 2019):
        #     prize = {
        #         'time': int(i),
        #         'id': 314,
        #     }
        #     for j in range(3):
        #         prize_temp = copy.deepcopy(prize)
        #         prize_temp['level'] = list(self.prize_level.values())[j]
        #
        #         yield scrapy.Request(self.url % (list(self.prize_level.keys())[j],str(i), 1), callback=self.parse_list, dont_filter=True,
        #                 meta={'prize': prize_temp, 'page':1})
        prize = {
            'time': '2020',
            'id': 314,
        }
        for j in range(3):
            prize_temp = copy.deepcopy(prize)
            prize_temp['level'] = list(self.prize_level.values())[j]
            yield scrapy.Request(self.url % (list(self.prize_level.keys())[j],'2020', 1), callback=self.parse_list,
                    meta={'prize': prize_temp, 'page':1})

    def parse_list(self, response):
        prize_data = response.meta['prize']
        page = response.meta['page']
        old_page_url = "page-{}.html".format(page)
        list_url = response.xpath('//ul[@id="worklist"]/li/a/@href').extract()
        for i in list_url:
            yield scrapy.Request(self.host + str(i), callback=self.parse_detail,
                                 meta={"prize": prize_data})
        next = response.xpath('//a[@class="arrow_right"]').extract()
        if next:
            page += 1
            new_page_url = "page-{}.html".format(page)
            yield scrapy.Request(response.url.replace(old_page_url, new_page_url), callback=self.parse_list,
                                 meta={'prize': prize_data, 'page': page})

    def parse_detail(self, response):
        item = DesignItem()
        prize = response.meta['prize']
        item['title'] = response.xpath('//div[@id="case_ms"]/h2/text()').extract()[0]
        description = response.xpath('//div[@class="ct_cn"]/p//text()').extract()
        item['description'] = ''.join(description)
        item['url'] = response.url
        item['evt'] = 3
        item['channel'] = "cgdaward"
        item['prize'] = json.dumps(prize, ensure_ascii=False)
        designer = ''
        try:
            designer_list = response.xpath('//div[@class="case_text"]//dl[2]/dd/p//text()').extract()
            for i in designer_list:
                m = re.findall('[\u4e00-\u9fa5]', i)
                if m:
                    designer = i
                    break
            if not designer:
                designer = designer_list[1]
        except:
            pass
        item['designer'] = designer
        customer = ''
        try:
            customer_list = response.xpath('//div[@class="case_text"]//dl[1]/dd/p//text()').extract()
            for i in customer_list:
                m = re.findall('[\u4e00-\u9fa5]', i)
                if m:
                    customer = i
                    break
            if not customer:
                customer = customer_list[1]
        except:
            pass
        item['customer'] = customer
        img_urls = list(set(response.xpath('//div[contains(@class,"swiper-slide")]/img/@src').extract()))
        for i in range(len(img_urls)):
            if not img_urls[i].startswith("http"):
                img_urls[i] = self.host + img_urls[i]
        item['img_urls'] = ','.join(img_urls)
        print(item)
        yield item
