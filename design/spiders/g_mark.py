# 日本G_MARK

import scrapy
import json, re
from design.items import DesignItem


class GMarkSpider(scrapy.spiders.Spider):
    name = "g_mark"

    url = "https://www.g-mark.org/award/search?from=&prizeCode=%s&keyword="

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

    level_list = {
        'GRAND': "Good Design Grand Award/优良设计大奖",
        'GOLD': 'Good Design Gold Award/优良设计金奖',
        'FUTURE_DESIGN': 'Good Focus Award [New Business Design]/优良设计焦点奖 [新商业活动设计]',
        'SME': 'Good Focus Award [Design of Technique & Tradition]/优良设计焦点奖 [技术&传承设计]',
        'JCCI': 'Good Focus Award [Design of Community Development]/优良设计焦点奖 [地域社会设计]',
        'JDP_CHAIRMAN': 'Good Focus Award [Disaster Prevention & Recovery Design]/优良设计焦点奖 [防灾&复兴设计]',
        'BEST100': 'Good Design Best 100/优良设计 Best 100',
        'LONGLIFE': 'Good Design Long Life Design Award/优良设计长效设计奖',
    }

    def start_requests(self):
        for i in self.level_list.keys():
            yield scrapy.Request(self.url % i, callback=self.parse_list, meta={"level": self.level_list[i]})

    def parse_list(self, response):
        level = response.meta['level']
        urls = response.xpath('//ul[contains(@class,"itemList")]/li/a[1]/@href').extract()
        urls.reverse()
        for url in urls:
            yield scrapy.Request('https://www.g-mark.org{}'.format(url), callback=self.item_deal, meta={'level': level})

    def item_deal(self, response):
        level = response.meta['level']
        item = DesignItem()
        item['url'] = response.url
        # 产品名称
        title = response.xpath("//dt/span[text()='Award-winning item']/following::dd[1]//text()").extract()
        if title:
            item['title'] = title[0]

        designer = response.xpath("//dt[text()='Designer']/following::dd[1]//text()").extract()
        if designer:
            item['designer'] = designer[0]
        description = response.xpath("//dl[@class='detail']/dt[text()='Outline']/following::dd[1]//text()").extract()
        if description:
            item['description'] = description[0]
        company = response.xpath("//dl[@class='detail']/dt[text()='Producer']/following::dd[1]//text()").extract()
        if company:
            item['company'] = ''.join(company).strip()
        # 产品网址
        remark = ''
        product_url = response.xpath(
            "//dl[@class='detail']/dt[text()='More information']/following::dd[1]//text()").extract()
        if product_url:
            remark += '产品地址:{}\n'.format(''.join(product_url).strip())
        # 产品制造商
        category = response.xpath("//dt/span[text()='Category']/following::dd[1]//text()").extract()
        if category:
            remark += '分类:{}\n'.format(''.join(category).strip())
        time = response.xpath(
            "//dl[@class='detail']/dt[text()='Already on the market']/following::dd[1]//text()").extract()
        if time:
            remark += '发布时间:{}\n'.format(''.join(time).strip())
        item['remark'] = remark
        item['evt'] = 3
        item['channel'] = 'g_mark'
        # 奖项
        # statement = response.xpath("//h3[text()='Evaluation']/following::div[1]//text()").extract()
        # prize_statement = ''
        # if statement:
        #     prize_statement = ''.join(statement[0]).strip()
        year = response.xpath("//h1[@class='year']/img/@alt").extract()[0]
        item['prize'] = json.dumps(
            {'id': 303, 'level': level, 'time': year},ensure_ascii=False)

        images = response.xpath('//ul[@class="thumnail"]/li//img/@src').extract()
        tmp_img = []
        if not images:
            images = response.xpath('//figure[@id="mainphoto"]//img/@src').extract()
        for image in images:
            tmp_img.append(re.sub('\?w=\d*&h=\d*', '?w=880&h=660', image))
        item['img_urls'] = ','.join(tmp_img)
        yield item

    def get_prize(self, level):
        prize_level = ''
        if level == '':
            prize_level = ''
        elif level == 'Good Design Award':
            prize_level = '好设计奖/Good Design Award'
        elif level == 'GOOD DESIGN｜グッドデザイン大賞':
            prize_level = 'Good Design Grand Award/优良设计大奖'
        elif level == 'GOOD DESIGN｜グッドデザイン金賞':
            prize_level = 'Good Design Gold Award/优良设计金奖'
        elif level == 'GOOD DESIGN｜グッドフォーカス賞 [新ビジネスデザイン]':
            prize_level = 'Good Focus Award [New Business Design]/优良设计焦点奖 [新商业活动设计]'
        elif level == 'GOOD DESIGN｜グッドフォーカス賞 [技術・伝承デザイン]':
            prize_level = 'Good Focus Award [Design of Technique & Tradition]/优良设计焦点奖 [技术&传承设计]'
        elif level == 'GOOD DESIGN｜グッドフォーカス賞 [地域社会デザイン]':
            prize_level = 'Good Focus Award [Design of Community Development]/优良设计焦点奖 [地域社会设计]'
        elif level == 'GOOD DESIGN｜グッドフォーカス賞［防災・復興デザイン］':
            prize_level = 'Good Focus Award [Disaster Prevention & Recovery Design]/优良设计焦点奖 [防灾&复兴设计]'
        elif level == 'GOOD DESIGN｜グッドデザイン・ベスト100':
            prize_level = 'Good Design Best 100/优良设计 Best 100'
        elif level == 'Good Design Long Life Design Award':
            prize_level = 'Good Design Long Life Design Award/优良设计长效设计奖'
        return prize_level
