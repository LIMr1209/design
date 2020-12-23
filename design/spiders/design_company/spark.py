# -*- coding: utf-8 -*-
import json
import urllib.parse
import scrapy
from design.items import DesignItem

data = {
    'channel': 'spark',
    'evt': 3,
    'company': '杭州斯帕克工业设计有限公司'
}


class ChinagoodSpider(scrapy.Spider):
    name = 'spark'
    cate_dict = {'9': '儿童用品', '10': '家用电器', '11': '智能装备', '12': '文化空间', '14': '护理'}
    cate_list = ['9', '10', '11', '12', '14']
    cate_index = 0
    page = 1
    url = 'http://www.spark-design.cn/ajax.asp?rnd=.7055475&s=case&page=%s&cid=%s' % (page, cate_list[cate_index])
    start_urls = [url]

    def parse(self, response):
        content = response.text
        result = json.loads(content)
        for i in result:
            item = DesignItem()
            item['title'] = i['title1']
            item['img_url'] = urllib.parse.unquote('http://www.spark-design.cn'+i['pic1'])
            item['url'] = 'http://www.spark-design.cn/zh-cn/caseshow/?id='+i['id']
            item['tags'] = self.cate_dict[self.cate_list[self.cate_index]]
            for key, value in data.items():
                item[key] = value
            yield item
        if content != '[]':
            self.page += 1
            yield scrapy.Request('http://www.spark-design.cn/ajax.asp?rnd=.7055475&s=case&page=%s&cid=%s' % (
            self.page, self.cate_list[self.cate_index]),callback=self.parse)
        else:
            if self.cate_index < 4:
                self.cate_index += 1
                self.page = 1
                yield scrapy.Request('http://www.spark-design.cn/ajax.asp?rnd=.7055475&s=case&page=%s&cid=%s' % (
                    self.page, self.cate_list[self.cate_index]), callback=self.parse)