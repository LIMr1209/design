import scrapy
from design.items import DesignItem
import json
import re
data = {
    'channel': 'artop',
    'evt': 3,
    'company': '上海浪尖工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'artop'
    allowed_domains = ['www.artop-sh.com']
    category = {'2cf03': '智能科技', '01e9b': '家居家电', '65962': '交通出行', '7e2c0': '机器人', '147e1': '机械自动化', '27ff8': '健康医疗','55fe6':'设计研究','99efd':'其他'}
    category_list = ['2cf03', '01e9b', '65962', '7e2c0', '147e1', '27ff8','55fe6','99efd']
    url = 'http://www.artop-sh.com/industrial#_case'
    start_urls = [url]


    def parse(self, response):
        for j in self.category_list:
            x = '//div[@class="row list-show"]/a[contains(@class,"%s")]' %j
            detail_list = response.xpath(x)
            for i in detail_list:
                item = DesignItem()
                url = 'http://www.artop-sh.com'+i.xpath('./@href').extract()[0]
                tags = self.category[j]
                title = i.xpath('./p/text()').extract()[0]
                # if not img_url.startswith('http'):
                #     img_url = 'http://www.artop-sh.com' + img_url
                item['title'] = title
                item['sub_title'] = title
                item['url'] = url
                item['tags'] = tags
                for key, value in data.items():
                    item[key] = value
                yield scrapy.Request(url=url,callback=self.parse_detail,meta={"item":item})

    def parse_detail(self,response):
        item = response.meta['item']
        url = response.url
        item['url'] = url
        img_urla = response.xpath('//section[@class="site-banner fn-full nonav"]//span/@data-src').extract()
        img_urlc = response.xpath('//section[@class="banner banner_text_right"]/img/@data-src').extract()
        img_urlb = response.xpath('//article[@class="content m-no full"]/img/@data-src').extract()
        img_urls = response.xpath('//div[@class="lightboxList container"]//a/@href').extract()
        img_urls.extend(img_urla)
        img_urls.extend(img_urlb)
        img_urls.extend(img_urla)
        img_urls.extend(img_urlc)
        remark = response.xpath('//div[@class="padding-md"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark).strip()
        if len(remark) > 480:
            remark = remark[:480]
        item['img_urls'] = ','.join(img_urls)
        item['remark'] = remark
        # print(item)
        yield item







