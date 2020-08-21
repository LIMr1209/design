import scrapy
from design.items import ProduceItem


class DesignCaseSpider(scrapy.Spider):
    name = 'veer'
    allowed_domains = ['www.veer.com']
    num = 0
    page = 1
    search = '保温杯'
    url = 'https://www.veer.com/query/image/?phrase=%s&page=%s' % (search, page)

    def start_requests(self):
        yield scrapy.Request(self.url, dont_filter=True)

    def parse(self, response):
        item = ProduceItem()
        img_url_list = response.xpath('//span[@class="search_result_asset_link"]/img//@src').extract()
        img_new_list = []
        for i in img_url_list:
            # j = i.replace('612', '1200')
            img_new_list.append(i)
        item['tag'] = self.search
        item['img_urls'] = img_new_list
        # yield item
        if self.page < 164:
            self.page += 1
            yield scrapy.Request(
                url="https://www.veer.com/query/image/?phrase=%s&page=%s" % (self.search, self.page),
                callback=self.parse)
