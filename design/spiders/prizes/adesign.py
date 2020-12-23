# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import parse_qs, urlparse

import scrapy
from design.items import DesignItem


data = {
    'channel': 'adesign',
    'evt': 3,
}


class ChinagoodSpider(scrapy.Spider):
    name = 'adesign'
    # 2010-2014
    # url = 'http://www.awardwinningdesign.org/'
    # 2015-2018
    url = 'https://www.awardeddesigns.com/'
    start_urls = [url]

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

    def parse(self, response):
        # detail_list = response.xpath('/html/body/div[@align="left"]/a/@href').extract()
        detail_list = response.xpath('//body/div/div[position()>2]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i,callback=self.parse_detail)
        # yield scrapy.Request('https://competition.adesignaward.com/design.php?ID=73247', callback=self.parse_detail)

    def parse_detail(self,response):
        item = DesignItem()
        text = response.xpath('/html/body/table[1]/tr[4]/td/span[4]/table/tr[2]/td[2]/h2/text()').extract()[0]
        rex = re.compile(r'Winner in (.*?)Design Category,')
        tags = rex.findall(text)[0]
        if tags.count('and'):
            tags = re.sub(r' and ',',',tags)
        rex = re.compile(r'Category, (\d+) - (\d+)')
        prize_time = rex.findall(text)
        prize_time = prize_time[0][1]
        url = response.url
        dest_str = urlparse(response.url)
        id = parse_qs(dest_str.query)['ID'][0]
        remark = ''
        img_url = response.xpath('//a[contains(@href,"{}")]/img/@src'.format(id)).extract()
        for i in range(len(img_url)):
            if img_url[i].startswith('.'):
                img_url[i] = img_url[i][1:]
            if not img_url[i].startswith('http'):
                if img_url[i].startswith('/'):
                    img_url[i] = 'https://competition.adesignaward.com' + img_url[i]
                else:
                    img_url[i] = 'https://competition.adesignaward.com/' + img_url[i]
        try:
            remark = response.xpath('/html/body/table[1]/tr[3]/td/table/tr[3]/td[1]//text()').extract()
            index = remark.index(" \r\nUNIQUE PROPERTIES / PROJECT DESCRIPTION:")
            remark = remark[index + 1]
            remark = remark.split('\r\n')
            remark = ' '.join(remark)
        except:
            print("*" * 100, remark, response.url)
            remark = ''

        title = response.xpath('/html/body/table[1]/tr[2]/td/table/tr/td[1]/h1/text()').extract()[0][:-4]
        designer = response.xpath('/html/body/table[1]/tr[2]/td/table/tr/td[1]/h1/a/text()').extract()[0].strip()
        item['title'] = title
        item['description'] = remark
        item['url'] = url
        item['img_urls'] = ','.join(img_url)
        item['designer'] = designer
        item['tags'] = tags
        prize = {
            'id': 312,
            'time': prize_time,
            'level': ''
        }
        item['prize'] = json.dumps(prize,ensure_ascii=False)
        for key, value in data.items():
            item[key] = value
        yield item
        # print(item)


