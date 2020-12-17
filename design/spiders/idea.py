# 美国工业IDAE

import scrapy
import json
from design.items import DesignItem
from lxml import etree
import time


class RedDotSpider(scrapy.spiders.Spider):
    name = "idea"
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
        # for page in range(0, 35):
        #     url = "https://www.idsa.org/awards/idea/gallery?term_node_tid_depth=All&field_year_value=All&field_idea_award_level_value=All&page={}".format(
        #         page)
        #     yield scrapy.Request(url, callback=self.body_response)
        #     break
        urls = ['https://www.idsa.org/awards/idea/digital-design/heffernan-icons', 'https://www.idsa.org/awards/idea/g-glass-compendium-skyline-design', 'https://www.idsa.org/awards/idea/naver-music-mobile-app','https://www.idsa.org/awards/idea/home/c-ge-smart-dimmer-switches']
        for url in urls:
            yield scrapy.Request(url, callback=self.item_deal)

    def body_response(self, response):
        urls = response.xpath('//div[@class="tile-container"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request('https://www.idsa.org{}'.format(url), callback=self.item_deal)
        # yield scrapy.Request("https://www.idsa.org/awards/idea/medical-scientific-products/samsung-xgeo-gu60",callback=self.item_deal)

    def item_deal(self, response):
        item = DesignItem()
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="l-content"]/h1/text()').extract()[0]
        item['evt'] = 3
        item['channel'] = 'idea'
        prize_level = response.xpath('//div[@class="fieldset-wrapper"]/div[1]/text()').extract()[0].strip()
        if prize_level == 'Bronze':
            prize_level = "Bronze/铜奖"
        elif prize_level == 'Gold':
            prize_level = "Gold/金奖"
        elif prize_level == 'Silver':
            prize_level = "Silver/银奖"
        elif prize_level == 'Featured Finalist':
            prize_level = "Featured Finalist/最终入围名单"
        prize_year = response.xpath('//div[@class="fieldset-wrapper"]/div[3]/text()').extract()[0].strip()
        item['prize'] = json.dumps({'id': 298, 'name': '美国IDEA工业设计奖', 'level': prize_level, 'time': prize_year},
                                   ensure_ascii=False)
        images = response.xpath("//div[@class='field--idea-image']//img/@src").extract()
        item['tags'] = response.xpath('//div[@class="fieldset-wrapper"]/div[2]//text()').extract()[0]
        res = response.xpath('//div[@class="field__item even"]//p').extract()
        item['description'] = ''
        for i in res:
            html = etree.HTML(i)
            a = html.xpath('//p/*')
            if not a:
                description = html.xpath('//p/text()')
                if not description:
                    continue
                item['description'] = description[0]
                break
            if a[0].tag == "br":
                description = html.xpath('//p/text()')
                item['description'] = "\n".join(description)
                break
        if not item['description']:
            try:
                description_list = response.xpath('//div[@class="field__item even"]/p[1]//text()').extract()
                item['description'] = ''.join(description_list)
            except:
                pass
        if not item['description']:
            try:
                description_list = response.xpath('//div[@class="field__item even"]/div[1]/p[1]//text()').extract()
                item['description'] = ''.join(description_list)
            except:
                pass
        if not item['description']:
            try:
                description_list = response.xpath('//div[@class="field__item even"]/div[1]/text()').extract()
                item['description'] = ''.join(description_list)
            except:
                pass
        if not item['description']:
            try:
                item['description'] = response.xpath('//span[@data-sheets-userformat]/text()').extract()[0]
            except:
                pass
        designer = response.xpath(
            '//div[@class="field__item even"]//strong[starts-with(text(),"Designe")]/../text()').extract()
        client = response.xpath(
            '//div[@class="field__item even"]//strong[starts-with(text(),"Client")]/../text()').extract()
        if client:
            item['customer'] = client[0].replace(":", '').strip()
        if designer:
            item['designer'] = designer[0].replace(":", '').strip()
        item['img_urls'] = ','.join(images)
        email = response.xpath('//div[@class="field__item even"]/p/a[text()="Email"]/@href').extract()
        remark = ''
        if email:
            remark = 'Email:' + email[0]
            remark += '\n'
        Website = response.xpath('//div[@class="field__item even"]/p/a[text()="Website"]/@href').extract()
        if Website:
            remark += 'Website:' + Website[0]
        if not item['description']:
            a = 1
        print(item['description'])
        item['remark'] = remark
        yield item
