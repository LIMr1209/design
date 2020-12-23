import scrapy
from design.items import DesignItem
import json
import re
data = {
    'channel': 'innozen',
    'evt': 3,
    'company': '深圳市意臣工业设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'innozen'
    allowed_domains = ['www.innozendesign.com']
    category = {1: '智能电子', 2: '家用电器', 3: '医疗器械', 4: '安防设备'}
    cate_index = 1
    url = 'http://www.innozendesign.com/index.php/Case/index/id/'+str(cate_index)+'.html'
    start_urls = [url]

    def parse(self, response):
        detail_list = response.xpath('//div[@class="item tcdiv"]/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.innozendesign.com'+i, callback=self.parse_detail)
        if self.cate_index < 4:
            self.cate_index += 1
            yield scrapy.Request('http://www.innozendesign.com/index.php/Case/index/id/'+str(self.cate_index)+'.html')

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        tags = self.category[self.cate_index]
        img_url = response.xpath('//div[@class="head_on"]/@style').extract()[0]
        rex = re.compile(r'url\((.*)\)')
        img_url = rex.findall(img_url)[0]
        img_urls = response.xpath('//div[@class="content_img"]/img/@src').extract()
        rex = re.compile(r'(/upfile/image/.+)')
        for i in range(len(img_urls)):
            img_urls[i] = rex.findall(img_urls[i])[0]

        img_urls.append(img_url)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.innozendesign.com'+img_urls[i]
        remark = response.xpath('//div[@class="content_a"]//text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ' '.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//div[@class="nami"]/text()').extract()[0]
        item['title'] = title
        item['remark'] = remark
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
