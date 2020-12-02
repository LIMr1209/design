# 台湾金点设计奖
import copy
import json

import scrapy
from lxml import etree

from design.items import DesignItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class JdsjSpider(scrapy.spiders.Spider):
    name = "jdsj"
    allowed_domains = ["goldenpin.org.tw"]
    url = 'https://www.goldenpin.org.tw/ft-admin/admin-ajax.php'
    refer = "https://www.goldenpin.org.tw/%s/?y=%s"
    prize = ['金點設計獎', '金點概念設計獎', '金點新秀設計獎']
    prize_id = ['15317', "53812", "53814"]
    year = '2014'
    prize_level = ['年度最佳设计奖']
    prize_level_id = ['198']
    data = {
        'action': 'presscore_template_ajax',
        'postID': '15317',
        'paged': '1',
        'targetPage': '1',
        'term': '199',
        'nonce': '30b6a36634',
        'contentType': 'portfolio',
        'pageData[type]': 'page',
        'pageData[template]': 'portfolio',
        'pageData[layout]': 'masonry',
        'sender': 'more'
    }


    def start_requests(self):
        for i in range(len(self.prize)):
            headers = {
                'Referer': self.refer % (self.prize[i], self.year)
            }
            data = copy.deepcopy(self.data)
            data['postID'] = self.prize_id[i]
            for j in range(len(self.prize_level)):
                tmp_data = copy.deepcopy(data)
                tmp_data['term'] = self.prize_level_id[j]
                yield scrapy.FormRequest(
                    url=self.url,
                    formdata=tmp_data,
                    headers=headers,
                    callback=self.parse_list,
                    dont_filter=True,
                    meta={'page': "1", "level": self.prize_level[j]}
                )

    def parse_list(self, response):
        html = json.loads(response)['html']
        res = etree.HTML(html)
        detail_list = res.xpath('//figure/a[1]/@href')




    def parse(self, response):
        item = DesignItem()
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="wf-wrap"]/descendant::h1[@class="entry-title"]/text()').extract()[
            0]
        item['evt'] = 7
        item['channel'] = 'jdsj'
        tmp_urls = response.xpath('//div[@class="shortcode-single-image"]/descendant::img/@data-src').extract()
        item['img_urls'] = ','.join(tmp_urls)
        prize = {'id': 6, 'name': '台湾金点奖', 'level': '', 'time': '2013'}
        print(prize)
        # item['prize'] = ujson.encode(prize, ensure_ascii=False)
        # yield item
