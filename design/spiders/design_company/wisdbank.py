import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'wisdbank',
    'evt': 3,
    'company': '大脑很行设计集团'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'wisdbank'
    allowed_domains = ['www.wisdbank.com']
    handle_httpstatus_list = [404, 500]
    start_urls = ['http://www.wisdbank.com/case/']
    cate_dict = {'shuma':'数码电子','jiexie':'机械设备','dianqi':'家用电器','yiliao':'医疗器械','lipin':'创意礼品'}
    cookie = {
        'Hm_lvt_9844f309666cda46cddbf08b0a9cc115': '1544609007, 1544609044',
        'Hm_lpvt_9844f309666cda46cddbf08b0a9cc115': '1544673800'
    }
    page = 1
    def parse(self, response):
        category_list = response.xpath('//ul[@class="sort"]/li/a/@href').extract()

        for i in category_list:
            self.page = 1
            yield scrapy.Request(i, callback=self.parse_category,cookies=self.cookie)


    def parse_category(self, response):
        old_url = response.url
        tags = old_url.split('/')
        cate = tags[len(tags)-2]
        tags = self.cate_dict[cate]
        detail_list = response.xpath('//div[@class="m_list"]/a')
        for i in detail_list:
            img_url = i.xpath('./img/@src').extract()[0]
            url = i.xpath('./@href').extract()[0]
            yield scrapy.Request(url,callback=self.parse_detail,meta={'img_url':img_url,'tags':tags})
        try:
            page = response.xpath('//div[@class="pageController clearfix"]/*[last()-1]/text()').extract()[0]
        except:
            page = 1
        if self.page < int(page):
            self.page += 1
            page_url = 'http://www.wisdbank.com/'+cate+'/index_'+str(self.page)+'.html'
            yield scrapy.Request(page_url,callback=self.parse_category)

    def parse_detail(self, response):
        item = DesignItem()
        img_urls = response.xpath(
            '//div[@class="right"]/div[@class="content"]//div[@class="content"]//img/@src').extract()
        url = response.url
        tags = response.meta.get('tags')
        title = response.xpath('//h1[@class="title"]/text()').extract()[0]
        item['title'] = title
        item['sub_title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(tags,self.page)
        yield item
