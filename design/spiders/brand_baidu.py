import json
import requests
import scrapy
from design.spiders.selenium import SeleniumSpider


class BrandSpider(SeleniumSpider):
    name = "brand_baidu"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'ITEM_PIPELINES': {
        },
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, key_words=None, *args, **kwargs):
        super(BrandSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        res = requests.get('http://dev.taihuoniao.com/api/brand/list')
        data = json.loads(res.content)['data']
        for i in data:
            name = i['name']
            id = i['id']
            if id == "202":
                url = "https://baike.baidu.com/item/JBL/6091174#viewPageContent"
            elif id == "190":
                url = "https://baike.baidu.com/item/%E5%BE%B7%E9%BE%99/22171551"
            elif id == "187":
                continue
            elif id == "183":
                url = 'https://baike.baidu.com/item/midori/1411018#viewPageContent'
            elif id == "182":
                continue
            elif id == "177":
                continue
            elif id == "176":
                url = "https://baike.baidu.com/item/DEVIALET"
            # elif int(id) < 177:
            #     continue
            else:
                url = "https://baike.baidu.com/item/%s" % name
            yield scrapy.Request(url, callback=self.parse_detail,
                                 meta={'usedSelenium': True, 'name': name, 'id': id})

    def parse_detail(self, response):
        item = dict()
        item['name'] = response.meta["name"]
        item['id'] = response.meta['id']
        try:
            item['en_name'] = response.xpath('//dt[contains(text(), "外文名")]/following-sibling::dd/text()').extract()[0].strip()
        except:
            pass
        try:
            item['found_time'] = response.xpath('//dt[contains(text(), "起")]/following-sibling::dd[1]/text()').extract()[0].strip()
        except:
            try:
                item['found_time'] = response.xpath('//dt[contains(text(), "成立时间")]/following-sibling::dd[1]/text()').extract()[0].strip()
            except:
                try:
                    item['found_time'] = response.xpath('//dt[contains(text(), "创立时间")]/following-sibling::dd[1]/text()').extract()[0].strip()
                except:
                    try:
                        item['found_time'] = response.xpath('//dt[contains(text(), "创始时间")]/following-sibling::dd[1]/text()').extract()[0].strip()
                    except:
                        pass
        try:
            item['img_url'] = response.xpath('//div[@class="summary-pic"]//img/@src').extract()[0]
        except:
            pass
        try:
            item['url'] = response.xpath('//dt[contains(text(), "官")]/following-sibling::dd[1]/text()').extract()[0].strip()
        except:
            pass
        try:
            item['country'] = response.xpath('//dt[contains(text(), "总部地点")]/following-sibling::dd[1]/text()').extract()[0].strip()[:2]
        except:
            try:
                item['country'] = response.xpath('//dt[contains(text(), "地")]/following-sibling::dd[1]/text()').extract()[0].strip()[:2]
            except:
                try:
                    item['country'] = response.xpath('//dt[contains(text(), "国")]/following-sibling::dd[1]/text()').extract()[0].strip()[:2]
                except:
                    pass
        if "country" in item and not item['country']:
            try:
                item['country'] = response.xpath('//dt[contains(text(), "总部地点")]/following-sibling::dd[1]/a/text()').extract()[
                                      0].strip()[:2]
            except:
                try:
                    item['country'] = \
                    response.xpath('//dt[contains(text(), "国")]/following-sibling::dd[1]/a/text()').extract()[
                        0].strip()[:2]
                except:
                    pass
        description_text = response.xpath('//div[@class="para-title level-2"]/following-sibling::div[@class="para"]//text()').extract()
        description = ''
        for i in description_text:
            j = i.strip()
            if not (j.startswith("[") and j.endswith("]")):
                j = ''.join(j.split())
                description += j
        item['description'] = description[:1000]
        res = requests.post('http://127.0.0.1:8004/api/brand/submit',data=item)
        print(res.content.decode("utf-8"))

