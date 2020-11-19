import scrapy
from design.items import DesignItem
import json



class CeidAwardSpider(scrapy.Spider):
    name = 'ceid-award'
    allowed_domains = ['www.ceid-award.cn/']
    url = 'http://www.ceid-award.cn/hjzp%s/index.jhtml'
    start_urls = [url]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES' : {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    def start_requests(self):
        for i in [2012,2016,2018]:
            prize = {}
            prize['time'] = str(i)
            prize['id'] = 307
            yield scrapy.Request(self.url %i, callback=self.parse_detail,meta={"prize":prize})

    def parse_detail(self, response):
        prize = response.meta['prize']
        url = response.url
        img_urls = response.xpath('//div[@class="plist2_img"]/img/@src').extract()
        titles = response.xpath('//div[@class="plist2_zi"]/p[1]/text()').extract()
        cu = response.xpath('//p[@class="plist2_zi_p1"]/text()').extract()
        for i in range(len(img_urls)):
            item = DesignItem()
            item['prize'] = json.dumps(prize, ensure_ascii=False)
            item['customer'] = cu[i]
            item['title'] = titles[i]
            item['img_urls'] = img_urls[i]
            item['url'] = url
            item['channel'] = 'ceid-award'
            item['evt'] = 3
            yield item
