# 韩国好设计奖
import scrapy
import re
from design.items import DesignItem
from .selenium import SeleniumSpider
import json ,time
from urllib.parse import urlparse, parse_qs
import datetime
datetime.timedelta()

class HghsjSpider(SeleniumSpider):
    name = "hghsj"
    allowed_domains = ["gd.kidp.or.kr"]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.SeleniumMiddleware': 543,
            # 'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES' : {
            'design.pipelines.ImagePipeline': 301,
        }
    }
    
    # start_urls = [
    # 	"http://gd.kidp.or.kr/product/product_list01.asp?page=&751&schYear=ALL&schPrize=&schCode=&schProduct=&search_id="
    # ]
    
    def start_requests(self):
        url = "http://gd.kidp.or.kr/product/product_list01.asp?page=%s&schYear=ALL&schPrize=&schCode=&schProduct=&search_id="
        for i in range(700, 1,-1):
            yield scrapy.Request(url=url % (i), callback=self.parse_list, meta={'usedSelenium': True})

    def parse_list(self, response):
        item_page_urls = response.xpath('//div[@class="w100"]/a/@href').extract()
        url = "http://gd.kidp.or.kr/product/%s"
        for item_page_url in item_page_urls:
            yield scrapy.Request(url=url % (item_page_url), callback=self.item_page,meta={'usedSelenium': True})

    def item_page(self, response):
        first_url = "http://gd.kidp.or.kr%s"
        item = DesignItem()
        item['title'] = response.xpath('//h4[@class="mgt40"]/text()').extract()[0]
        item['url'] = response.url
        item['evt'] = 3
        item['tags'] = response.xpath('//table[@class="tb01 mgt10 infotbl forpc"]/descendant::tr[4]/td[1]/text()').extract()[0]
        item['company'] = response.xpath('//table[@class="tb01 mgt10 infotbl forpc"]/descendant::tr[5]/td[1]/text()').extract()[0]
        item['designer'] = ','.join(response.xpath('//table[@class="tb01 mgt10 infotbl forpc"]/descendant::tr/td[2]/text()').extract())
        try:
            item['description'] =  response.xpath('//*[@id="productextbl"]/tr[2]/td/text()').extract()[0].strip()
        except:
            pass
        item['channel'] = "hghsj"
        # 　奖项
        prize = {'id': 304, 'level': '', 'time':''}
        # prize = {"id":395,'level': '','time': ''}
        time_str = response.xpath('//table[@class="tb01 mgt10 infotbl forpc"]/descendant::tr[1]/td[1]/strong/text()').extract()[0]
        data = time_str.split(' ')
        level = data[1]
        time = data[0][:4]
        prize['time'] = time
        prize['level'] = level if level != '선정' else ''
        item['prize'] = json.dumps(prize,ensure_ascii=False)

        img_url = []
        img_urls = response.xpath('//div[@class="img-preview"]/img/@src').extract()
        if not img_urls:
            a = 1
        dest_str = urlparse(response.url)

        for tmp_url in img_urls:
            if "_SMALL(0)" in tmp_url:
                img_url.append(first_url % (tmp_url.replace('_SMALL(0)', '')))
            elif "_SMALL(2)" in tmp_url:
                img_url.append(first_url % (tmp_url.replace('_SMALL(2)', '')))
            elif "_SMALL(1)" in tmp_url:
                img_url.append(first_url % (tmp_url.replace('_SMALL(1)', '')))
            elif "_SMALL" in tmp_url:
                img_url.append(first_url % (tmp_url.replace('_SMALL', '')))
            elif "T0" in tmp_url:
                img_url.append(first_url % (tmp_url.replace('T0', 'P0').replace('/T/','/P/')))
            elif tmp_url and tmp_url != '/':
                img_url.append(first_url % (tmp_url))
            if tmp_url and  parse_qs(dest_str.query)['idx'][0] not in tmp_url:
                b = 1
        item['img_urls'] = ','.join(img_url)
        yield item
        # print(item)