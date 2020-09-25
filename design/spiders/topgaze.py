# -*- coding: utf-8 -*-
import json

import scrapy
from design.items import DesignItem

data = {
    'channel': 'topgaze',
    'evt': 3,
    'company': '北京上品极致产品设计有限公司'
}


class ChinagoodSpider(scrapy.Spider):
    name = 'topgaze'
    typeid = 18 # 19,20,21,22,23
    page = -1
    url = 'http://www.topgaze.net/plus/listajax.php?typee=anli&typeid='+str(typeid)+'&startpage='+str(page)
    flag = False

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            callback=self.parse,
        )


    def parse(self, response):
        if self.flag:
            detail_list = response.xpath('//div[@class="iui-transition product"]/a/@href').extract()
            for i in detail_list:
                # print('http://www.topgaze.net'+i)
                yield scrapy.Request('http://www.topgaze.net'+i.strip(),callback=self.parse_detail)

            if detail_list:
                self.page += 1
                yield scrapy.FormRequest(
                    url='http://www.topgaze.net/plus/listajax.php?typee=anli&typeid='+str(self.typeid)+'&startpage='+str(self.page),
                    callback=self.parse,
                )
            else:
                if self.typeid < 23:
                    self.page = -1
                    self.typeid += 1
                    yield scrapy.FormRequest(
                        url='http://www.topgaze.net/plus/listajax.php?typee=anli&typeid='+str(self.typeid)+'&startpage='+str(self.page),
                        callback=self.parse,
                    )
        else:
            self.flag = True
            yield scrapy.FormRequest(
                url=self.url,
                callback=self.parse,
                dont_filter=True
            )



    def parse_detail(self,response):
        item = DesignItem()
        title = response.xpath('//h2[@class="title"]/text()').extract()[0]
        tags = response.xpath('//li[@class="active"]/a/text()').extract()[0]
        remark = response.xpath('//div[@class="iui-wrap iui-auto product-details-content"]/p/text()').extract()

        remark = [''.join(i.split()) for i in remark]
        remark = ','.join(remark)
        img_urls = response.xpath('//div[@class="iui-wrap iui-auto product-details-content"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.topgaze.net' + img_urls[i]
        url = response.url
        item['title'] = title
        item['sub_title'] = title
        item['tags'] = tags
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        item['remark'] = remark
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item