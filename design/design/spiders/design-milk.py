import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'milk',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'designmilk'
    allowed_domains = ['design-milk.com']
    page = 1
    url = 'https://design-milk.com/category/technology'
    start_urls = [url]

    def parse(self,response):
        detail_list = response.xpath('//div[@class="col-md-4 col-sm-6 col-xs-12 article-list-item"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i,callback=self.parse_detail)
        if self.page < 135:
            self.page += 1
            yield scrapy.Request(url=self.url+'/page/'+str(self.page)+'/')

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        try:
            img_url = response.xpath('//img[@class="actual-image"]/@src').extract()[0]
        except:
            img_url = response.xpath('//div[@class="content-column"]/p[2]/a/img/@src').extract()[0]
        img_urls = response.xpath('//div[@class="content-column"]/div[@id]/a/img/@src').extract()
        img_urls.append(img_url)
        if not img_url.startswith('https://design-milk.com'):
            img_url = 'https://design-milk.com'+img_url
        title = response.xpath('//h1/text()').extract()[0]
        if len(title) > 99:
            title = title[:99]
        remark = ','.join(response.xpath('//div[@class="content-column"]/p[1]//text()').extract())
        try:
            if not remark:
                remark = ','.join(response.xpath('//div[@class="content-column"]/p[2]//text()').extract())
            if len(remark) > 450:
                remark = remark[:450]
        except:
            remark = ''
        item['tags'] = 'technology'
        item['title'] = title.strip()
        item['sub_title'] = title.strip()
        item['remark'] = remark.replace('\n', '').replace('\n\r', '').strip()
        item['url'] = url
        item['img_urls'] = ','.join(img_urls)
        # print('标题',title)
        # print('图片地址', img_url)
        # print('原文地址', url)
        # print('备注',remark)
        for key, value in data.items():
            item[key] = value
        yield item

