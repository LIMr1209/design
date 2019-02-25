import scrapy
from design.items import DesignItem
import json

data = {
    'channel': 'kickstar',
    'evt': 3,
}


class DesignCaseSpider(scrapy.Spider):
    name = 'kickstarter'
    allowed_domains = ['www.kickstarter.com']
    page = 1
    category_ids = {
        '331': '3D Printing',
        '332': 'Apps',
        '333': 'Camera Equipment',
        '334': 'DIY Electronics',
        '335': 'Fabrication Tools',
        '336': 'Flight',
        '337': 'Gadgets',
        '52': 'Hardware',
        '362': 'Makerspaces',
        '338': 'Robots',
        '51': 'Software',
        '339': 'Sound',
        '340': 'Space Exploration',
        '341': 'Wearables',
        '342': 'Web',
        '343': 'Candles',
        '344': 'Crochet',
        '345': 'DIY',
        '346': 'Embroidery',
        '347': 'Glass',
        '348': 'Knitting',
        '351': 'Printing',
        '352': 'Quilts',
        '353': 'Stationery',
        '354': 'Taxidermy',
        '355': 'Weaving',
        '356': 'Woodworking',
        '25': 'Architecture',
        '259': 'Civic Design',
        '27': 'Graphic Design',
        '260': 'Interactive Design',
        '28': 'Product Design',
        '261': 'Typography'
    }
    index_ids = ['332','333', '334', '335', '336','337', '52', '362', '338', '51', '339', '340', '341', '342','25','259','27','260','28','261','343', '344', '345', '346', '347', '348', '351', '352', '353', '354', '355', '356']
    index_id = 0
    category_id = index_ids[index_id]
    start_urls = [
        'https://www.kickstarter.com/discover/advanced?category_id=' + category_id + '&sort=magic&seed=2573000&page=' + str(
            page)]

    def parse(self, response):
        date = response.xpath('//div[@class="grid-row flex flex-wrap"]/div[@data-project]/@data-project').extract()
        for i in date:
            item = DesignItem()
            dic = json.loads(i)
            url = dic['urls']['web']['project']
            img_url = dic['photo']['1536x864']
            if self.category_id in ['332','333', '334', '335', '336','337', '52', '362', '338', '51', '339', '340', '341', '342']:
                tags = "Technology," + self.category_ids[self.category_id]
            elif self.category_id in ['25','259','27','260','28','261']:
                tags = 'Design' + self.category_ids[self.category_id]
            else:
                tags = 'Crafts' + self.category_ids[self.category_id]
            item['img_url'] = img_url.strip()
            item['tags'] = tags
            item['url'] = url
            item['info'] = i
            yield scrapy.Request(url, callback=self.parse_detail, meta={'item': item})

        if date:
            if self.page < 200:
                self.page += 1
                yield scrapy.Request(
                    'https://www.kickstarter.com/discover/advanced?category_id=' + self.category_id + '&sort=magic&seed=2573000&page=' + str(
                        self.page))
            else:
                self.page = 1
                self.index_id += 1
                self.category_id = self.index_ids[self.index_id]
                yield scrapy.Request(
                    'https://www.kickstarter.com/discover/advanced?category_id=' + self.category_id + '&sort=magic&seed=2573000&page=' + str(
                        self.page))
        else:
            self.page = 1
            self.index_id += 1
            self.category_id = self.index_ids[self.index_id]
            yield scrapy.Request(
                'https://www.kickstarter.com/discover/advanced?category_id=' + self.category_id + '&sort=magic&seed=2573000&page=' + str(
                    self.page))

    def parse_detail(self, response):
        item = response.meta['item']
        try:
            designer = response.xpath(
                '//div[@class="col-full flex items-center flex-column-md items-start-md mb3 order-2-md col-md-4-24 col-sm-22-24"]/span/a/text()').extract()[
                0]
            title = response.xpath('//div[@class="col-20-24 block-md order-2-md col-lg-14-24"]/h2/text()').extract()[0]
            remark = response.xpath('//div[@class="col-20-24 block-md order-2-md col-lg-14-24"]/p/text()').extract()[0]
        except IndexError as e:
            designer = \
                response.xpath('//a[@class="hero__link remote_modal_dialog js-update-text-color"]/text()').extract()[0]
            title = response.xpath('//span[@class="relative"]/a/text()').extract()[0]
            remark = \
                response.xpath('//span[@class="content edit-profile-blurb js-edit-profile-blurb"]/text()').extract()[0]
        item['designer'] = designer.strip()
        item['title'] = title.strip()
        item['remark'] = remark.strip().replace('\n', '').replace('\n\r', '')
        for key, value in data.items():
            item[key] = value
        yield item
