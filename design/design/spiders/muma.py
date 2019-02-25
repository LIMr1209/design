import scrapy
from design.items import DesignItem
import json
import re
data = {
    'channel': 'muma',
    'evt': 3,
    'company': '上海木马工业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'muma'
    allowed_domains = ['www.designmoma.com']
    start_urls = ['http://www.designmoma.com/industrial.html']
    page = 1

    def parse(self, response):
        category_list = response.xpath('//*[@id="myTab"]/li[position()>1]/a')
        for i in category_list:
            self.page = 1
            cate_id = i.xpath('./@href').extract()[0]
            cate_id = re.search(r'\d+',cate_id).group()
            tags = i.xpath('./text()').extract()[0]
            url = i.xpath('./@href').extract()[0]
            yield scrapy.Request('http://www.designmoma.com'+url, callback=self.parse_category,meta={'cate_id':cate_id,'tags':tags})

    def parse_category(self,response):
        tags = response.meta['tags']
        cate_id = response.meta['cate_id']
        detail_list = response.xpath('//li[@class="iasli"]/div/a/@href').extract()
        for i in detail_list:
            yield scrapy.Request('http://www.designmoma.com'+i,callback=self.parse_detail,meta={'tags':tags})
        try:
            page = response.xpath('//nav[@class="pagination"]/ul/*[last()-1]//text()').extract()[0]
        except:
            page = 1
        if self.page < int(page):
            self.page += 1
            yield scrapy.Request('http://www.designmoma.com/industrial/'+cate_id+'-'+str(self.page)+'.html',callback=self.parse_category,meta={'cate_id':cate_id,'tags':tags})



    def parse_detail(self, response):
        tags = response.meta.get('tags')
        print(tags,self.page)
        item = DesignItem()
        url = response.url
        img_urls = response.xpath('//div[@class="c-detailbanner"]/img/@src').extract()
        img_urls.extend(response.xpath('//div[@class="carousel-inner"]//img/@src').extract())
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http'):
                img_urls[i] = 'http://www.designmoma.com' + img_urls[i]
        remark = response.xpath('//div[@class="cdetail-text fl"]/p/text()').extract()
        remark = [''.join(i.split()) for i in remark]
        remark = ''.join(remark)
        if len(remark) > 500:
            remark = remark[:500]
        title = response.xpath('//div[@class="cdetail-name fl"]/h1/text()').extract()[0]
        title = title.replace('\r\n','').strip()
        item['title'] = title
        item['remark'] = remark
        item['sub_title'] = title
        item['img_urls'] = ",".join(img_urls)
        item['url'] = url
        item['tags'] = tags
        for key, value in data.items():
            item[key] = value
        yield item
