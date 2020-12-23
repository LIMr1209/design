import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'yinheid',
    'evt': 3,
    'company': '深圳市银河工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'yinheid'
    allowed_domains = ['www.yinheid.com']
    category = {'zhinenzhifu': 'PI设计', 'yiliaoqixie': '新零售', 'jiqiren': '消费升级', 'zhinenkongjing': '工业4.0', 'gongyeyiqi': '智慧医疗', 'dianziyan': '机器人','zhinenanfang':'产业互联网','xiaofeidianzi':'用户体验设计'}
    category_list = ['zhinenzhifu', 'yiliaoqixie', 'jiqiren', 'zhinenkongjing', 'gongyeyiqi', 'dianziyan','zhinenanfang','xiaofeidianzi']
    category_index = 0
    url = 'http://www.yinheid.com/'+category_list[category_index]+'/'
    start_urls = [url]
    page = 1

    def parse(self, response):
        detail_list = response.xpath('//ul[@class="no-list-style cases-list2 row"]/li/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.yinheid.com'+i, callback=self.parse_detail)
        try:
            page = response.xpath('//div[@class="page"]/ul/li[last()-1]/a/text()').extract()[0]
        except:
            page = 1
        if self.page < int(page):
            self.page += 1
            url = 'http://www.yinheid.com/'+self.category_list[self.category_index]+'/'+response.xpath('//div[@class="page"]/ul/li[last()]/a/@href').extract()[0]

            yield scrapy.Request(url=url,callback=self.parse)
        else:
            if self.category_index < 7:
                self.page = 1
                self.category_index += 1
                yield scrapy.Request('http://www.yinheid.com/'+self.category_list[self.category_index]+'/',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        if tags == "用户体验设计":
            tags = ''
        img_urls = response.xpath('//div[@class="case-detail-box"]//img/@src').extract()
        img_urls.pop(0)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.yinheid.com' + img_urls[i]

        remark = response.xpath('//div[@class="prointro"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//h3[@class="title"]/text()').extract()[0]
        item['title'] = title
        item['sub_title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        print(item)
        yield item
