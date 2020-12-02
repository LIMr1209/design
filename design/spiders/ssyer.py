import json

import scrapy
from design.items import DesignItem
import re


# 2016 319  2015  309  2014 286 2013 301 2012 277 2011 247 2010 203 2009 100 2008 143 2007 105 2006 19
class DesignCaseSpider(scrapy.Spider):
    name = 'ssyer'
    allowed_domains = ['www.ssyer.com']
    year = 2019
    yearid = 'undefined'
    year_list = {
        '2017': "6281", "2018": "7223", "2019": "undefined",
        '2016': '5452', '2015': '4475', '2014': '3398', '2013': '2653', '2012': '804',
        '2011': '803', '2010': '802', '2009': '807', '2008': '808', '2007': '809', '2006': '810'
    }
    cmd = 'getProList'
    type = 0
    url = 'http://www.redstaraward.org/ajax/AjaxHandler_HXJGW_GW.ashx'
    prize_levels = ['至尊金奖', '银奖', '原创奖金奖', '原创奖', '金奖', '红星奖', '原创奖银奖']
    total = 1

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.DesignDownloaderMiddleware': 543,
        }
    }

    def start_requests(self):
        # FormRequest 是Scrapy发送POST请求的方法
        for i in self.prize_levels:
            yield scrapy.FormRequest(
                url=self.url,
                formdata={"cmd": self.cmd, "page": "1", "yearid": self.yearid, 'type': str(self.type),
                          'key': i},
                callback=self.parse,
                dont_filter=True,
                meta={'page': "1", 'prize_level': i}
            )

    def parse(self, response):
        page = int(response.meta['page'])
        prize_level = response.meta['prize_level']
        content = response.body.decode('utf-8')
        rex = re.compile(r'(/content/details.+?html)')
        result = list(set(rex.findall(content)))
        for i in result:
            yield scrapy.Request(url="http://www.redstaraward.org/" + i, callback=self.parse_detail, dont_filter=True)
        if result:
            page += 1
            yield scrapy.FormRequest(
                url=self.url,
                formdata={"cmd": self.cmd, "page": str(page), "yearid": self.yearid, 'type': str(self.type),
                          'key': prize_level},
                callback=self.parse,
                dont_filter=True,
                meta={'page': str(page), 'prize_level': prize_level}
            )

    def parse_detail(self, response):
        url = response.url
        self.total += 1
        item = DesignItem()
        img_url = response.xpath('//div[@class="only"]/img/@src').extract()[0]
        if not img_url.startswith('http://www.redstaraward.org'):
            img_url = 'http://www.redstaraward.org/' + img_url
        try:
            title = response.xpath('//div[@class="zuopin_h"][1]/div/text()').extract()[0]
        except:
            title = ''
        try:
            designer = response.xpath('//div[@class="zuopin_h"][2]/div/text()').extract()[0]
        except:
            designer = ''
        try:
            company = response.xpath('//div[@class="zuopin_h"][3]/div/text()').extract()[0]
        except:
            company = ''
        try:
            remark = response.xpath('//div[@class="zuopin_h"][6]/div/text()').extract()[0]
        except:
            remark = ''
        try:
            prize_level = response.xpath('//div[@class="zuopin_h"][4]/div/text()').extract()[0]
        except:
            prize_level = ''
        if title == '说明':
            return
        item['img_urls'] = img_url.strip()
        item['title'] = title.strip()
        item['company'] = company.strip()
        prize = {}
        prize['time'] = str(self.year)
        prize['id'] = 299
        prize['level'] = "红星" + prize_level if prize_level.startswith('原创') else prize_level
        item['description'] = remark
        item['prize'] = json.dumps(prize)
        item['designer'] = designer.strip()
        item['url'] = url.strip()
        item['evt'] = 3
        item['channel'] = 'redstar'
        print("总数", self.total)
        yield item
