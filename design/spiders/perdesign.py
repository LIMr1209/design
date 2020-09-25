# -*- coding: utf-8 -*-
import json

import scrapy
from design.items import DesignItem

data = {
    'channel': 'perdesign',
    'evt': 3,
    'company': '品物商业创新设计集团'
}


class ChinagoodSpider(scrapy.Spider):
    name = 'perdesign'
    url = 'http://www.perdesigncn.com/Home/listspage'
    p = 1

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            formdata={'p': str(self.p)},
            callback=self.parse,
        )

    def parse(self, response):
        date = json.loads(response.body)
        for i in date['data']:
            item = DesignItem()
            title = i['title']
            tags = ''
            try:
                for cate in i['showcateList']:
                    tags += cate['name']+','
            except:
                tags = ''
            img_url = 'http://www.perdesigncn.com'+i['litpic']
            url = 'http://www.perdesigncn.com/Home/info/'+i['id']
            info = i
            item['title'] = title
            item['tags'] = tags
            item['url'] = url
            item['img_url'] = img_url
            for key, value in data.items():
                item[key] = value
            item['info'] = i
            yield item
        if self.p < 9:
            self.p += 1
            try:
                yield scrapy.FormRequest(
                    url=self.url,
                    formdata={'p': str(self.p)},
                    callback=self.parse
                )
            except:
                print(self.p,'*'*50)

