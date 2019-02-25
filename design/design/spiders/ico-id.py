import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'ico-id',
    'evt': 3,
    'company': '爱谷工业设计公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'ico-id'
    allowed_domains = ['www.ico-id.com']
    category = {'11': '医疗设备', '10': '实验仪器', '12': '动力机械', '13': '园林工具', '14': '个人消费', '15': '工业设备','16':'其他案例'}
    category_list = ['10','11', '12', '13', '14', '15', '16']
    category_index = 0
    url = 'http://www.ico-id.com/class/view?id='+category_list[category_index]
    start_urls = [url]


    def parse(self, response):
        detail_list = response.xpath('//div[@class="mach"]/ul/li/a')
        for i in detail_list:
            url = i.xpath('./@href').extract()[0]
            title = i.xpath('./img/@title').extract()[0]
            yield scrapy.Request(url, callback=self.parse_detail,meta={'title':title})

        if self.category_index < 6:
            self.category_index += 1
            yield scrapy.Request(url ='http://www.ico-id.com/class/view?id='+self.category_list[self.category_index],callback=self.parse)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = ''
        if self.category[self.category_list[self.category_index]] != '其他案例':
            tags = self.category[self.category_list[self.category_index]]
        img_urls = response.xpath('//div[@class="about"]/div[3]/img/@src').extract()
        img_url = response.xpath('//div[@class="nr"]/table/tbody/tr[2]/td/img/@src').extract()[0]
        img_urls.append(img_url)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.ico-id.com' + img_urls[i]
        title = response.meta.get('title')
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
