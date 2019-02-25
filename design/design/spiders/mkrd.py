import scrapy
from design.items import DesignItem

data = {
    'channel': 'mike',
    # 'channel': '瑞得',
    'name': '',
    'tags': '',
    'color_tags': '',
    'brand_tags':'',
    'material_tags': '',
    'style_tags': '',
    'technique_tags': '',
    'other_tags': '',
    'user_id': 0,
    'kind': 1,
    'brand_id': 0,
    'prize_id': -1,
    'prize': '',
    'evt': 3,
    'prize_level': '',
    'prize_time': '',
    'category_id': 0,
    'status': 1,  # 状态
    'deleted': 0,  # 是否软删除
    'info': '',
    'company': '米可创新工业设计(北京)有限责任公司',
    # 'company': '瑞得胜嘉（北京）科技有限公司',
    'designer': ''
}


class DesignCaseSpider(scrapy.Spider):
    name = 'mikeruide'
    allowed_domains = ['http://www.mkdesign.cn']
    start_urls = ['http://www.mkdesign.cn/Work.html']

    def parse(self, response):
        a_list = response.xpath('//a/@href').extract()
        design_list = []
        for i in a_list:
            if i not in ['HOME.html','#']:
                if i.startswith('Work In/'):
                    i = i.replace('Work In/','')
                    design_list.append(i)
        for design in design_list:
            yield scrapy.Request('http://www.mkdesign.cn/'+design, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        url = response.url
        item = DesignItem()
        img_url = response.xpath('//table[3]//img/@src').extract()[0]
        if not img_url.startswith('http://www.mkdesign.cn/'):
            img_url = 'http://www.mkdesign.cn/' + img_url
        message = response.xpath('//table[2]//p/text()').extract()[0]
        title = message.split('|')[0]
        try:
            remark = message.split('|')[1]
        except:
            message = response.xpath('//table[2]//p/text()').extract()[1]
            title = message.split('|')[0]
            remark = message.split('|')[1]
        item['url'] = url
        item['img_url'] = img_url.strip()
        item['title'] = title.strip()
        item['remark'] = remark.strip()
        for key, value in data.items():
            item[key] = value
        yield item
