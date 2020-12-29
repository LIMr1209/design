# 美国工业IDAE

import scrapy
import json
from design.items import DesignItem
from lxml import etree


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
    category_list = [
        {'name': 'Commercial & Industrial Products', 'tag': '商业和工业产品', 'opalus_id': 276},
        {'name': 'Consumer Technology', 'tag': '', 'opalus_id': 276},
        {'name': 'Communication Tools', 'tag': '通讯工具', 'opalus_id': 276},
        {'name': 'Computer Equipment', 'tag': '计算机设备', 'opalus_id': 276},
        {'name': 'Design Strategy', 'opalus_id': 276},
        {'name': 'Digital Design', 'tag': '数码设计', 'opalus_id': 276},
        {'name': 'Digital Interaction', 'opalus_id': 276},
        {'name': 'Interactive Product Experiences', 'tag': '互动产品体验', 'opalus_id': 276},
        {'name': 'Entertainment', 'tag': '娱乐', 'opalus_id': 276},
        {'name': 'Automotive & Transportation', 'tag': '汽车&交通', 'opalus_id': 282},
        {'name': 'Kitchen & Accessories', 'tag': '厨房&配件', 'opalus_id': 278},
        {'name': 'Kitchens', 'tag': '厨房', 'opalus_id': 278},
        {'name': 'Medical & Health', 'opalus_id': 284},
        {'name': 'Medical & Scientific Products', 'tag': '医疗和科学产品', 'opalus_id': 284},
        {'name': "Children's Products", 'tag': '儿童产品', 'opalus_id': 285},
        {'name': 'Lifestyle & Accessories', 'opalus_id': 285},
        {'name': 'Personal Accessories', 'tag': '个人配件', 'opalus_id': 285},
        {'name': 'Gardens & Patio', 'tag': '花园&庭院', 'opalus_id': 285},
        {'name': 'Home Furnishings', 'tag': '家装', 'opalus_id': 281},
        {'name': 'Living Room & Bedroom', 'tag': '客厅&卧室', 'opalus_id': 281},
        {'name': 'Environments', 'tag': '环境', 'opalus_id': 277},
        {'name': 'Office & Accessories', 'opalus_id': '277'},
        {'name': 'Office & Productivity', 'tag': '办公&生产力', 'opalus_id': 277},
        {'name': 'Home', 'opalus_id': 281},
        {'name': 'Bathrooms, Spas, Wellness', 'tag': '卫浴、温泉、健康', 'opalus_id': 316},
        {'name': 'Home & Bath', 'tag': '家居&卫浴', 'opalus_id': 316},
        {'name': 'Furniture & Lighting', 'tag': '家具&照明', 'opalus_id': 288},
        {'name': 'Sports, Leisure & Recreation', 'tag': '体育、休闲&娱乐', 'opalus_id': 289},
        {'name': 'Outdoor & Garden', 'opalus_id': 290},
        {'name': 'Outdoor Products', 'tag': '户外用品', 'opalus_id': 290},
        {'name': 'Branding', 'tag': '品牌建设', 'opalus_id': 317},
        {'name': 'Research', 'tag': '研究', 'opalus_id': 317},
        {'name': 'Packaging', 'opalus_id': 317},
        {'name': 'Packaging & Graphics', 'tag': '包装&图形', 'opalus_id': 317},
        {'name': 'Service Design', 'tag': '服务设计', 'opalus_id': 317},
        {'name': 'Social Impact Design', 'opalus_id': 317},
        {'name': 'Ecodesign', 'tag': '生态设计', 'opalus_id': 317},
        {'name': 'Student Designs', 'tag': '学生设计', 'opalus_id': 317}

    ]

    def start_requests(self):
        for page in range(0, 35):
            url = "https://www.idsa.org/awards/idea/gallery?term_node_tid_depth=All&field_year_value=All&field_idea_award_level_value=All&page={}".format(
                page)
            yield scrapy.Request(url, callback=self.body_response)

    #
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
        category = response.xpath('//div[@class="fieldset-wrapper"]/div[2]//text()').extract()[0]
        if category:
            for j in self.category_list:
                if category == j['name']:
                    item['category_id'] = j['opalus_id']
                    item['tags'] = j['tags'] if 'tags' in j else ''
                    break
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
        if category:
            remark += '分类:' + category
            remark += '\n'
        Website = response.xpath('//div[@class="field__item even"]/p/a[text()="Website"]/@href').extract()
        if Website:
            remark += 'Website:' + Website[0]
        if not item['description']:
            a = 1
        print(item['description'])
        item['remark'] = remark
        yield item
