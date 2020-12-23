# 德国红点设计奖
import copy
from urllib.parse import urlparse, parse_qs
import scrapy
import json, requests
import urllib.parse
from design.items import DesignItem


def stringToDict(cookie):
    cookies = {}
    items = cookie.split(';')
    for item in items:
        key = item.split('=')[0].replace(' ', '')
        value = item.split('=')[1]
        cookies[key] = value
    return cookies


class RedDotSpider(scrapy.spiders.Spider):
    name = "red_dot_2"
    allowed_domains = ["red-dot.org"]
    page = 1
    cookie = stringToDict(
        'site-langua|ge-preference=1; _ga=GA1.2.554486985.1603193165; CookieConsent={stamp:%27kKk+E+22SaoD+HijQyWJKqNefkCiRcIeUjaaH4MaBH8JIkEW4fYP5g==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:false%2Cver:1%2Cutc:1603193171598%2Cregion:%27cn%27}; _gid=GA1.2.1619988625.1603678049')
    host = "https://www.red-dot.org"
    prize_level = ["Red Dot", "Red Dot: Best of the Best", "Red Dot: Honourable Mention"]
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

    url = "https://www.red-dot.org/search?tx_solr[filter][0]=result_type:online_exhibition&tx_solr[filter][1]=online_exhibition_type:Product Design&tx_solr[filter][3]=%s&tx_solr[filter][5]=%s&tx_solr[page]=%s&type=7383"

    def start_requests(self):
        # for i in range(2020, 2010, -1):
        #     prize = {
        #         'time': str(i),
        #         'id': 1
        #     }
        #     yield scrapy.Request(self.url % ("year:" + str(i), '', '', ''), callback=self.parse, dont_filter=True,
        #                          cookies=self.cookie, meta={'prize': prize})
        prize = {
            'time': str(2011),
            'id': 1
        }
        # for j in self.prize_level:
        #     prize['level'] = j
        #     print("页码", 1)
        #     print(prize)
        #     yield scrapy.Request(
        #         self.url % ("year:" + prize['time'], "awards:" + prize['level'], 1),
        #         dont_filter=True, cookies=self.cookie, callback=self.parse_list,
        #         meta={"prize": prize, "page": 1})
        prize['level'] = self.prize_level[2]
        print("页码", 1)
        print(prize)
        yield scrapy.Request(
            self.url % ("year:" + prize['time'], "awards:" + prize['level'], 1),
            dont_filter=True, cookies=self.cookie, callback=self.parse_list,
            meta={"prize": prize, "page": 1})

    def parse_list(self, response):
        from lxml import etree
        html = etree.HTML(response.text)
        prize_data = response.meta['prize']
        list_url = html.xpath('//a[@class="search-link"]/@href')
        for i in list_url:
            yield scrapy.Request(self.host + str(i), dont_filter=True, cookies=self.cookie, callback=self.parse_detail,
                                 meta={"prize": prize_data})
        try:
            all_page = int(html.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()')[0])
        except:
            all_page = 0
        page = response.meta["page"]
        if page < all_page:
            page += 1
            print("页码", page)
            print(prize_data)
            yield scrapy.Request(self.url % (
                "year:" + prize_data['time'], "awards:" + prize_data["level"], page),
                                 dont_filter=True, cookies=self.cookie, callback=self.parse_list,
                                 meta={"prize": response.meta['prize'], "page": page})
        else:
            print(prize_data, "总页书", page)
    def parse_detail(self, response):
        item = DesignItem()
        prize = response.meta['prize']
        item['title'] = response.xpath('//h1[@class="h2"]/text()').extract()[0]
        item['description'] = response.xpath('//div[@class="description"]/text()').extract()[0]
        item['url'] = response.url
        if item["url"] == 'https://www.red-dot.org/project/nvidia-spot-1-12068':
            print(1)
        item['evt'] = 3
        item['channel'] = "www_red_dot"
        prize_data = copy.deepcopy(prize)
        if prize['level'] == "Red Dot":
            prize_data['level'] = "红点奖/Winner"
        elif prize['level'] == "Red Dot: Best of the Best":
            prize_data['level'] = "最佳设计奖/Best of the Best"
        else:
            prize_data['level'] = "佳作奖/Honourable Mention"
        statement = response.xpath('//div[@class="statement"]//p[2]//text()').extract()
        prize['statement'] = statement[0] if statement else ""
        item['prize'] = json.dumps(prize_data, ensure_ascii=False)
        values = response.xpath('//div[@class="value"]//text()').extract()
        keys = response.xpath('//div[@class="label"]/text()').extract()
        data = {keys[i]:j  for i,j in enumerate(values)}
        for i in data.items():
            if i[0] == "Manufacturer":
                item['customer'] = i[1]
            elif i[0] == "Design":
                item['company'] = i[1]
            elif i[0] == "In-house design":
                item['designer'] = i[1]
        if "designer" not in item or item['designer'] == "":
            item['designer'] = ''
        if "company" not in item or item['company'] == "":
            item['company'] = ''
        if "customer" not in item or item['customer'] == "":
            item['customer'] = ''
        try:
            img_url = response.xpath('//img[@class="lazy"]/@data-src').extract()[0].replace("amp;", '')
        except:
            img_url = ""
        item['img_urls'] = [img_url]
        img_detail = response.xpath('//img[@class="owl-lazy"]/@data-src').extract()
        if img_detail:
            item['img_urls'].append(img_detail[0].replace("amp;", ''))
        item['img_urls'] = ','.join(item['img_urls'])
        brand_url = response.xpath('//div[@class="links"]//a/@href').extract()
        # 设计团队网站
        item['remark'] = '品牌/设计公司网址:{}\n'.format(','.join(brand_url))
        item['remark'] = '{}产品图片下载地址:{}'.format(item['remark'], img_url)
        # print(item)
        yield item