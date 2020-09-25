import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'bifoxs',
    'evt': 3,
    'company': '深圳市白狐工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'bifoxs'
    allowed_domains = ['www.bifoxs.com']
    category_list = ['6', '7', '8', '9', '10', '11','16']
    category_index = 0
    page = 1
    url = 'http://www.bifoxs.com/case-2-'+category_list[category_index]+'.html'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//div[@id="caseCon"]/ul/li/a/@href').extract()
        tags = response.xpath('//*[@class="plTitle"]/h2/text()').extract()[0]
        for i in detail_list:
            yield scrapy.Request('http://www.bifoxs.com/'+i, callback=self.parse_detail,meta={'tags':tags})
        try:
            page = response.xpath('//div[@class="yema"]/*[last()-1]/text()').extract()[0]
        except:
            page = 1
        if self.page < int(page):
            self.page += 1
            yield scrapy.Request('http://www.bifoxs.com/caselist.aspx?bcate=2&scate='+self.category_list[self.category_index]+'&pm='+str(self.page))
        else:
            if self.category_index < 6:
                self.page = 1
                self.category_index += 1
                yield scrapy.Request('http://www.bifoxs.com/case-2-'+self.category_list[self.category_index]+'.html',callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        # print(self.category_list[self.category_index],self.page ,"***********")
        url = response.url
        tags = response.meta.get('tags')
        if tags == '综合其它':
            tags = ''
        img_url = response.xpath('//img[@class="proXqPic plMg"]/@src').extract()[0]
        img_urls = response.xpath('//div[@class="bd"]//img/@src').extract()
        img_urls.append(img_url)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.bifoxs.com' + img_urls[i]
        remark = response.xpath('//div[@class="plFd"][2]/text()').extract()[0]
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        # try:
        #     remark = response.xpath('//*[@id="wrapContainer"]/div[3]/table/tbody/tr[2]/td[2]/span/text()').extract()[0]
        # except:
        #     try:
        #         remark = response.xpath('//tr[@class="firstRow"]/td[1]/p/span/text()').extract()[0]
        #     except:
        #         remark = response.xpath('//*[@id="wrapContainer"]/div[3]/table/tbody/tr[2]/td[2]//text()').extract()
        #         remark = [''.join(i.split()) for i in remark]
        #         remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//div[@class="plFd"]/h2/text()').extract()
        title = [''.join(i.split()) for i in title]
        title = ''.join(title)
        item['title'] = title
        item['remark'] = remark
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
