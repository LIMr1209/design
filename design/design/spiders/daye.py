import scrapy
from design.items import DesignItem
import re

data = {
    'channel': 'daye',
    'evt': 3,
    'company': '广州市大业产品设计有限公司'
}


class DesignCaseSpider(scrapy.Spider):
    name = 'daye'
    allowed_domains = ['www.daye.hk']
    page = 1
    start_urls = ['http://www.daye.hk/index.php/product/index/cid/52']

    cookie = {'PHPSESSID': '14cganorfau6ttphsk2psaaup2',
              'Hm_lvt_6c2de4005be4351afdf3523fe08e46a8': '1544150482',
              'Hm_lvt_ebaf62f9bf47e7c47e2ee3b304e6a3d6': '1544150482',
              'think_language': 'zh-CN',
              'Hm_lpvt_6c2de4005be4351afdf3523fe08e46a8': '1544173968',
              'Hm_lpvt_ebaf62f9bf47e7c47e2ee3b304e6a3d6': '1544173968'}

    def start_requests(self):
        yield scrapy.Request(url='http://www.daye.hk/index.php/product/index/cid/52', cookies=self.cookie,
                             callback=self.parse)

    def parse(self, response):
        category_list = response.xpath('//div[@class="col-md-8 sub_nav"]/ul/li')
        for i in category_list:
            tags = i.xpath('./a/text()').extract()[0]
            url = i.xpath('./a/@href').extract()[0]

            yield scrapy.Request('http://www.daye.hk' + url, cookies=self.cookie,callback=self.parse_list, meta={'tags': tags})

    def parse_list(self, response):
        category_url = response.url
        tags = response.meta['tags']
        detail_list = response.xpath('//div[@class="case-box-image col-md-3 mb40"]//h3/a')
        for i in detail_list:
            url = i.xpath('./@href').extract()[0]
            title = i.xpath('./text()').extract()[0]
            yield scrapy.Request('http://www.daye.hk' + url, callback=self.parse_detail, meta={'tags': tags,'title':title})
        try:
            page = int(response.xpath('//ul[@class="pagination top"]/li[last()]/a/text()').extract()[0])
        except:
            try:
                page = int(response.xpath('//ul[@class="pagination top"]/li[last()-1]/a/text()').extract()[0])
            except:
                page = 1
        if self.page < page:
            self.page += 1
            page_url = category_url+'/p/'+str(self.page)
            yield scrapy.Request(url=page_url + '/p/' + str(self.page), cookies=self.cookie,callback=self.parse_list,meta={'tags':tags})

    def parse_detail(self, response):
        item = DesignItem()
        url = response.url
        title = response.meta['title']
        img_url = response.xpath('//div[@class="case-show"]/@style').extract()[0]
        rex = re.compile(r'url\(\'(.*?)\'\)')
        img_url = rex.findall(img_url)[0]
        img_urls = response.xpath('//div[@class="content-page product"]//img/@src').extract()
        img_urls.append(img_url)
        for i in range(len(img_urls)):
            if not img_urls[i].startswith('http://www.daye.hk'):
                img_urls[i] = 'http://www.daye.hk' + img_urls[i]
        tags = response.meta['tags']
        if tags == 'More...':
            tags = ''
        item['tags'] = tags
        item['img_urls'] = ','.join(img_urls)
        item['sub_title'] = title
        item['url'] = url
        item['title'] = title
        for key, value in data.items():
            item[key] = value
        # print(item)
        yield item
        # print(img_urls)