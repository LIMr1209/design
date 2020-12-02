# 台湾金点设计奖
import json

import scrapy
from design.items import DesignItem


class JdsjSpider(scrapy.spiders.Spider):
    name = "jdsj-new"
    allowed_domains = ["goldenpin.org.tw"]
    url = 'https://www.goldenpin.org.tw/project-category/%s/page/%s/'
    prize_level = ['年度最佳设计奖', '年度特别奖循环设计奖', '年度特别奖社会设计奖', '金点概念设计奖年度最佳设计奖', '金点新秀设计奖年度最佳设计奖']
    prize_level_dict = {
        '年度最佳設計獎-金點': '年度最佳设计奖',
        '年度特別獎循環設計獎-金點': '年度特别奖循环设计奖',
        '年度特別獎社會設計獎-金點': '年度特别奖社会设计奖',
        '年度最佳設計獎-概念獎': '金点概念设计奖年度最佳设计奖',
        '年度最佳設計獎-新秀獎': '金点新秀设计奖年度最佳设计奖'
    }
    prize_level_list = ['年度最佳設計獎-金點','年度特別獎循環設計獎-金點', '年度特別獎社會設計獎-金點', '年度最佳設計獎-概念獎', '年度最佳設計獎-新秀獎']

    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.DesignDownloaderMiddleware': 543,
        }
    }

    def start_requests(self):
        for i in self.prize_level_list:
            yield scrapy.Request(self.url%(i,1), callback=self.parse_list, meta={'page': 1,'level':i})

    def parse_list(self, response):
        page = response.meta['page']
        level = response.meta['level']
        detail_list = response.xpath('//figure/a[1]/@href').extract()
        for i in detail_list:
            yield scrapy.Request(i, callback=self.parse_detail, meta={'level': level})
        page += 1
        yield scrapy.Request(self.url%(level,page), callback=self.parse_list, meta={'page': page,'level':level})

    def parse_detail(self, response):
        level = response.meta['level']
        item = DesignItem()
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="wf-wrap"]/descendant::h1[@class="entry-title"]/text()').extract()[
            0]
        item['evt'] = 3
        item['channel'] = 'jdsj'
        tmp_urls = response.xpath('//div[contains(@class,"shortcode-single-image-wrap alignnone")]//img/@data-src').extract()
        item['img_urls'] = ','.join(tmp_urls)
        prize_time = response.xpath('//ol/a[2]/text()').extract()[0]
        prize = {'id': 300, 'level': self.prize_level_dict[level], 'time': prize_time}
        try:
            customer = response.xpath('//span[contains(text(),"產品廠商")]/following-sibling::strong[1]/span/text()').extract()
            item['customer'] = customer[0]
        except:
            pass
        try:
            designer = response.xpath('//span[contains(text(),"設計師 ")]/strong/span/text()').extract()
            item['designer'] = ''.join(designer).strip()
        except:
            pass
        item['prize'] = json.dumps(prize)
        # print(item)
        yield item
#