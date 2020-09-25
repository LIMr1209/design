import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'ctdesign',
    'evt': 3,
    'company': '江苏创品工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'ctdesign'
    allowed_domains = ['www.ctdesign.cn']
    category = {'124': '家用电器', '122': '工业设备', '121': '智能家电', '120': '医疗', '119': '母婴','118':'消费电子'}
    category_list = ['124', '122', '121', '120', '119','118']
    category_index = 0
    url = 'http://www.ctdesign.cn/case.asp?Pone='+category_list[category_index]+'#yes'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//ul[@class="ca_img clearfix"]/li[position()>1]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.ctdesign.cn/'+i, callback=self.parse_detail,dont_filter=True)
        if self.category_index < 5:
            self.category_index += 1
            yield scrapy.Request('http://www.ctdesign.cn/case.asp?Pone='+self.category_list[self.category_index]+'#yes',callback=self.parse,dont_filter=True)

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = self.category[self.category_list[self.category_index]]
        img_urls = response.xpath('//div[@class="ci_p"]//img/@src').extract()
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.ctdesign.cn' + img_urls[i][1:]
        title = response.xpath('//div[@class="ci_head clearfix"]/span/text()').extract()[0][3:]
        item['title'] = title
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
