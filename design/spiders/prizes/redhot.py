# 德国红点设计奖
import copy
from urllib.parse import urlparse, parse_qs
import scrapy
import json, requests

from pydispatch import dispatcher
from scrapy import signals

from design.items import DesignItem


def stringToDict(cookie):
    cookies = {}
    items = cookie.split(';')
    for item in items:
        key = item.split('=')[0].replace(' ', '')
        value = item.split('=')[1]
        cookies[key] = value
    return cookies


class RedDotSpider(scrapy.spiders.Spider):
    name = "red_dot"
    # allowed_domains = ["red-dot.org"]
    cookie = stringToDict(
        'site-langua|ge-preference=1; _ga=GA1.2.554486985.1603193165; CookieConsent={stamp:%27kKk+E+22SaoD+HijQyWJKqNefkCiRcIeUjaaH4MaBH8JIkEW4fYP5g==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:false%2Cver:1%2Cutc:1603193171598%2Cregion:%27cn%27}; _gid=GA1.2.1619988625.1603678049')
    host = "https://www.red-dot.org"
    prize_level = ["Red Dot", "Red Dot: Best of the Best", "Red Dot: Honourable Mention"]
    category_list = [
        {'name': ['Audio'], 'opalus_id': 276, 'tag': '音频'},
        {'name': ['Cameras and Camera Equipment', 'Cameras and camera equipment', 'Cameras',
                  'Drones and action cameras', 'Consumer electronics and cameras'], 'opalus_id': 276, 'tag': '相机&摄像设备'},
        {'name': ['Communication Technology', 'Communication technology', 'Communication'], 'opalus_id': 276,
         'tag': '通信技术'},
        {'name': ['Computer and Information Technology', 'Computer and information technology',
                  'Computers and information technology'], 'opalus_id': 276,
         'tag': '计算机&信息技术'},
        {'name': ['Bicycles and Bicycle Accessories', 'Bicycles and bicycle accessories',
                  'Bicycle and bicycle accessories'], 'opalus_id': 282,
         'tag': '自行车&自行车配件'},
        {'name': ['Cars and Motorcycles', 'Cars and motorcycles'], 'opalus_id': 282, 'tag': '汽车&摩托车'},
        {'name': ['Commercial Vehicles', 'Commercial vehicles'], 'opalus_id': 282, 'tag': '商用车'},
        {'name': ['Motorhomes and Caravans', 'Motorhomes and caravans'], 'opalus_id': 282, 'tag': '房车&大篷车'},
        {'name': ['Trains and Planes', 'Ships,trains and planes'], 'opalus_id': 282, 'tag': '火车&飞机'},
        {'name': ['Vehicle Accessories', 'Vehicle accessories', 'Vehicles and vehicles accessories'], 'opalus_id': 282,
         'tag': '车辆配件'},
        {'name': ['Watercraft'], 'opalus_id': 282, 'tag': '水上交通工具'},
        {'name': ['Industrial Equipment,Machinery and Automation', 'Industrial equipment,machinery and automation'],
         'opalus_id': 280, 'tag': '工业设备、机械&自动化'},
        {'name': ['Materials and Surfaces', 'Materials and surfaces'], 'opalus_id': 280, 'tag': '材料&表面'},
        {'name': ['Tools'], 'opalus_id': 280, 'tag': '工具'}, {'name': ['Robotics'], 'opalus_id': 280, 'tag': '机器人技术'},
        {'name': ['Cookware and Cooking Utensils', 'Cookware and cooking utensils'], 'opalus_id': 278,
         'tag': '炊具&烹饪用具'},
        {'name': ['Kitchen Appliances and Kitchen Accessories', 'Kitchen appliances and kitchen accessories'],
         'opalus_id': 278, 'tag': '厨房电器&厨房配件'},
        {'name': ['Kitchen Taps and Sinks', 'Kitchen taps and sinks'], 'opalus_id': 278, 'tag': '厨房&厨房家具'},
        {'name': ['Kitchens and Kitchen Furniture', 'Kitchens and kitchen furniture', 'Kitchens'], 'opalus_id': 278,
         'tag': '厨房水龙头和水槽'},
        {'name': ['Tableware', 'Tableware and cooking utensils'], 'opalus_id': 278, 'tag': '厨房&厨房家具'},
        {'name': ['Healthcare'], 'opalus_id': 284, 'tag': '医疗保健'},
        {'name': ['Life sciences and medicine', 'Life science and medicine'], 'opalus_id': 284, 'tag': '生命科学&医学'},
        {'name': ['Medical Devices and Technology', 'Medical devices and technology'], 'opalus_id': 284,
         'tag': '医疗设备&技术'},
        {'name': ['Babies and Children', 'Babies and children'], 'opalus_id': 285, 'tag': '婴儿&儿童'},
        {'name': ['Fashion and Lifestyle Accessories', 'Fashion and lifestyle accessories',
                  'Fashion,lifestyle and accessories', ], 'opalus_id': 285,
         'tag': '时尚&生活用品'},
        {'name': ['Garden Appliances,Garden Tools and Garden Equipment',
                  'Garden appliances,garden tools and garden equipment'], 'opalus_id': 285,
         'tag': '花园用具，工具&设备'},
        {'name': ['Glasses'], 'opalus_id': 285, 'tag': '玻璃杯'},
        {'name': ['Hobby and Leisure', 'Hobby and leisure', 'Leisure,sport and fun'], 'opalus_id': 285, 'tag': '爱好&休闲'},
        {'name': ['Jewellery'], 'opalus_id': 285, 'tag': '首饰'},
        {'name': ['Luggage and Bags', 'Luggage and bags'], 'opalus_id': 285, 'tag': '行李&包'},
        {'name': ['Personal Care,Wellness and Beauty', 'Personal care,wellness and beauty',
                  'Personal Care, wellness and beauty', 'Personal care, wellness and beauty',
                  'Personal Care,Wellness und Beauty'], 'opalus_id': 285,
         'tag': '个人护理、健康&美容'},
        {'name': ['Watches'], 'opalus_id': 285, 'tag': '手表'},
        {'name': ['Watches and jewellery'], 'opalus_id': 285, 'tag': '手表&首饰'},
        {'name': ['Bedroom furniture'], 'opalus_id': 281, 'tag': '卧室家具'},
        {'name': ['Bedroom Furniture and Beds', 'Bedroom furniture and beds'], 'opalus_id': 281, 'tag': '卧室家具&床'},
        {'name': ['Garden furniture', 'Garden'], 'opalus_id': 281, 'tag': '花园家具'},
        {'name': ['Home and Seating Furniture', 'Home and seating furniture', 'Home furniture'], 'opalus_id': 281,
         'tag': '家居&座椅家具'},
        {'name': ['Interior Architecture and Interior Design', 'Interior architecture and interior design'],
         'opalus_id': 281, 'tag': '室内建筑&室内设计'},
        {'name': ['Interior Design Elements', 'Interior design elements', 'Interior design'], 'opalus_id': 281,
         'tag': '室内设计元素'},
        {'name': ['Office Furniture and Office Chairs', 'Office furniture and office chairs'], 'opalus_id': 277,
         'tag': '办公家具&办公椅'},
        {'name': ['Office Supplies and Stationery', 'Office supplies and stationery', 'Office furniture', 'Offices'],
         'opalus_id': 277, 'tag': '办公用品&文具'},
        {'name': ['Urban Design', 'Urban design', 'Urban design and public spaces'], 'opalus_id': 277,
         'tag': '城市设计/Urban Design'},
        {'name': ['TV and Home Entertainment', 'TV and home entertainment'], 'opalus_id': 279, 'tag': '电视&家庭娱乐'},
        {'name': ['Heating and Air Conditioning Technology', 'Heating and air conditioning technology',
                  'Heating and air conditioning'], 'opalus_id': 286,
         'tag': '加热&空调技术'},
        {'name': ['Household Appliances and Household Accessories', 'Household appliances and household accessories'],
         'opalus_id': 286, 'tag': '家用电器&电器配件'},
        {'name': ['Bathroom Taps and Shower Heads', 'Bathroom taps and shower heads'], 'opalus_id': 316,
         'tag': '浴室水龙头&淋浴喷头'},
        {'name': ['Bathroom and Sanitary Equipment', 'Bathroom and sanitary equipment',
                  'Bathroom and sanitary furniture', 'Bathrooms and spas'],
         'opalus_id': 316,
         'tag': '浴室&卫生设备'},
        {'name': ['Lighting and Lamps', 'Lighting and lamps'], 'opalus_id': 288, 'tag': '照明&灯具'},
        {'name': ['Sports Equipment', 'Sports equipment'], 'opalus_id': 289, 'tag': '体育器材'},
        {'name': ['Outdoor and Camping Equipment', 'Outdoor and camping equipment'], 'opalus_id': 290,
         'tag': '户外&露营设备'},
        {'name': ['Mobile Phones,Tablets and Wearables', 'Mobile phones,tablets and wearables'], 'opalus_id': 291,
         'tag': '移动电话、平板&可穿戴'},
        {'name': ['Innovative Products'], 'opalus_id': 317, 'tag': '创新产品'},
        {'name': ['Smart Products'], 'opalus_id': 291, 'tag': '智能产品'}
    ]
    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    url = "https://www.red-dot.org/search?tx_solr[filter][0]=result_type:online_exhibition&tx_solr[filter][1]=online_exhibition_type:Product Design&tx_solr[filter][3]=%s&tx_solr[filter][4]=%s&tx_solr[filter][5]=%s&tx_solr[page]=%s"

    def start_requests(self):
        for i in range(2011, 2021):
            prize = {
                'time': str(i),
                'id': 296
            }
            yield scrapy.Request(self.url % ("year:" + str(i), '', '', ''), callback=self.parse, dont_filter=True,
                                 cookies=self.cookie, meta={'prize': prize})

    def __init__(self, *args, **kwargs):
        dispatcher.connect(receiver=self.mySpiderCloseHandle,
                           signal=signals.spider_closed
                           )

        super(RedDotSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        from lxml import etree
        html = etree.HTML(response.text)
        prize_data = response.meta['prize']
        category_url = html.xpath('//*[@id="facet-categories"]/option/@value')
        category_url = category_url[1:]
        for i in category_url:
            query = urlparse(str(i)).query
            data = dict([(k, v[0]) for k, v in parse_qs(query).items()])
            category = data['tx_solr[filter][6]'].split(':')[1]
            for j in self.prize_level:
                prize = copy.deepcopy(prize_data)
                prize['level'] = j
                yield scrapy.Request(
                    self.url % ("year:" + prize_data['time'], "categories:" + category, "awards:" + str(j), ''),
                    dont_filter=True, cookies=self.cookie, callback=self.parse_list,
                    meta={"category": category, "prize": prize, "page": 1})

    def parse_list(self, response):
        from lxml import etree
        html = etree.HTML(response.text)
        prize_data = response.meta['prize']
        page = response.meta["page"]
        category = response.meta['category']
        list_url = html.xpath('//a[@class="search-link"]/@href')
        # print("页码", page)
        # print(prize_data, category)
        for i in list_url:
            prize = copy.deepcopy(prize_data)
            yield scrapy.Request(self.host + str(i), dont_filter=True, cookies=self.cookie, callback=self.parse_detail,
                                 meta={"category": response.meta['category'], "prize": prize})
        try:
            all_page = int(html.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()')[0])
        except:
            all_page = 0

        if page < all_page:
            page += 1
            yield scrapy.Request(self.url % (
                "year:" + prize_data['time'], "categories:" + category, "awards:" + prize_data["level"], page),
                                 dont_filter=True, cookies=self.cookie, callback=self.parse_list,
                                 meta={"category": category, "prize": response.meta['prize'], "page": page})

    def parse_detail(self, response):
        item = DesignItem()
        prize = response.meta['prize']
        item['title'] = response.xpath('//h1[@class="h2"]/text()').extract()[0]
        item['description'] = response.xpath('//div[@class="description"]/text()').extract()[0]
        item['url'] = response.url
        item['evt'] = 3
        item['channel'] = "www_red_dot"
        if prize['level'] == "Red Dot":
            prize['level'] = "Red Dot/红点奖"
        elif prize['level'] == "Red Dot: Best of the Best":
            prize['level'] = "Red Dot: Best of the Best/红点最佳设计奖"
        else:
            prize['level'] = "Red Dot: Honourable Mention/红点荣誉奖"
        statement = response.xpath('//div[@class="statement"]//p[2]//text()').extract()
        prize['statement'] = statement[0] if statement else ""
        item['prize'] = json.dumps(prize, ensure_ascii=False)
        try:
            for j in self.category_list:
                if response.meta['category'] in j['name']:
                    item['category_id'] = j['opalus_id']
                    item['tags'] = j['tag']
                    break
        except:
            pass
        values = response.xpath('//div[@class="value"]//text()').extract()
        keys = response.xpath('//div[@class="label"]/text()').extract()
        data = {keys[i]: j for i, j in enumerate(values)}
        for i in data.items():
            if i[0] == "Manufacturer":
                item['customer'] = i[1]
            elif i[0] == "Design":
                item['company'] = i[1]
            elif i[0] == "In-house design":
                item['designer'] = i[1]
        if "designer" not in item or item['designer'] == "":
            item['designer'] = ''
        if "company" not in item or item['company'] == "":
            item['company'] = ''
        if "customer" not in item or item['customer'] == "":
            item['customer'] = ''
        item['img_urls'] = []
        img_url = response.xpath('//img[@class="lazy"]/@data-src').extract()
        if img_url:
            item['img_urls'].append(img_url[0].replace("amp;", '').replace('usage=hero', 'usage=overview'))
        img_detail = response.xpath('//img[@class="owl-lazy"]/@data-src').extract()
        if img_detail:
            item['img_urls'].append(img_detail[0].replace("amp;", ''))
        item['img_urls'] = ','.join(item['img_urls'])
        brand_url = response.xpath('//div[@class="links"]//a/@href').extract()
        # 设计团队网站
        item['remark'] = '品牌/设计公司网址:{}\n'.format(','.join(brand_url))
        item['remark'] = '{}产品图片下载地址:{}\n'.format(item['remark'], img_url)
        item['remark'] = '{}分类:{}'.format(item['remark'], response.meta['category'])
        self.crawler.stats.inc_value('suc_count')
        # # print(item)
        yield item

    def mySpiderCloseHandle(self, spider):
        pass
