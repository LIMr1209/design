# 日本G_MARK

import scrapy
import json, re
from design.items import DesignItem


class GMarkSpider(scrapy.spiders.Spider):
    name = "g_mark"

    url = "https://www.g-mark.org/award/search?from=&prizeCode=%s&keyword="

    category_list = [
        {'name': 'Accessories for smartphones, personal computers and cameras', 'tag': '智能手机、个人电脑和相机配件',
         'opalus_id': 276, },
        {'name': 'Audio equipment and music instruments', 'tag': '音响设备和乐器', 'opalus_id': 276, },
        {'name': 'Cameras, mobile phones and tablets', 'tag': '照相机、手机和平板电脑', 'opalus_id': 276, },
        {'name': 'Video equipment', 'tag': '视频设备', 'opalus_id': 276, },
        {'name': 'Broadcast and sound equipment for professional use', 'tag': '专业用途广播和音响设备', 'opalus_id': 276, },
        {'name': 'ICT equipment for the general public', 'tag': '面向公众信息和通信技术设备', 'opalus_id': 276, },
        {'name': 'ICT equipment for professional use', 'tag': '专业使用信息和通信技术设备', 'opalus_id': 276, },
        {'name': 'Passenger car, Passenger car-related instruments', 'tag': '乘用车、乘用车相关仪器', 'opalus_id': 282, },
        {'name': 'Commercial vehicle, Commercial vehicle-related instruments', 'tag': '商用车, 商用车相关仪器',
         'opalus_id': 282, },
        {'name': 'Motorbike, Motorbike-related instruments', 'tag': '摩托车, 摩托车相关设备', 'opalus_id': 282, },
        {'name': 'Personal mobility and bicycle, Personal mobility and bicycle-related instruments',
         'tag': '个人移动和自行车, 个人移动和自行车相关工具', 'opalus_id': 282, },
        {'name': 'Railway, Shipping, Aircraft', 'tag': '铁路、航运、飞机', 'opalus_id': 282, },
        {'name': 'Transportation system and service (logistics / physical distribution)', 'tag': '运输系统和服务(物流/实物配送)',
         'opalus_id': 282, },
        {'name': 'Working tools and instruments', 'tag': '工作工具和仪器', 'opalus_id': 280, },
        {'name': 'Agricultural tools and equipment', 'tag': '农业工具和设备', 'opalus_id': 280, },
        {'name': 'Equipment and facilities for production and manufacturing', 'tag': '生产和制造设备和设施', 'opalus_id': 280, },
        {'name': 'Materials and parts', 'tag': '材料和部件', 'opalus_id': 280, },
        {'name': 'Manufacturing and production technique', 'tag': '制造和生产技术', 'opalus_id': 280, },
        {'name': 'Equipment and facilities for research and experiment', 'tag': '研究和实验的设备和设施', 'opalus_id': 280, },
        {'name': 'Kitchen goods, cookware, tableware and cutlery', 'tag': '厨房用品、炊具、餐具和刀叉', 'opalus_id': 278, },
        {'name': 'Kitchen fixtures', 'tag': '厨房设备', 'opalus_id': 278, },
        {'name': 'Kitchen equipment and facilities for professional use', 'tag': '专业厨房设备和设施', 'opalus_id': 278, },
        {'name': 'Health care items', 'tag': '保健用品', 'opalus_id': 284, },
        {'name': 'Household nursing and rehabilitation equipment', 'tag': '家庭护理和康复设备', 'opalus_id': 284, },
        {'name': 'Medical equipment and facilities', 'tag': '医疗设备和设施', 'opalus_id': 284, },
        {'name': 'Accessories and personal items', 'tag': '配件和个人物品', 'opalus_id': 285, },
        {'name': 'Clothing', 'tag': '服装', 'opalus_id': 285, },
        {'name': 'Sanitary goods', 'tag': '卫生用品', 'opalus_id': 285, },
        {'name': 'Childcare goods and accessories', 'tag': '儿童保育用品及配件', 'opalus_id': 285, },
        {'name': 'Household childcare items', 'tag': '家庭育儿用品', 'opalus_id': 285, },
        {'name': 'Hobby goods and pet care supplies', 'tag': '爱好用品和宠物护理用品', 'opalus_id': 285, },
        {'name': 'Garden tools', 'tag': '花园工具', 'opalus_id': 285, },
        {'name': 'Daily necessities', 'tag': '日用品', 'opalus_id': 285, },
        {'name': 'Home furniture', 'tag': '家庭家具', 'opalus_id': 281, },
        {'name': 'Cleaning goods', 'tag': '清洁用品', 'opalus_id': 281, },
        {'name': 'Emergency supplies', 'tag': '应急用品', 'opalus_id': 281, },
        {'name': 'Bedclothes', 'tag': '床上用品', 'opalus_id': 281, },
        {'name': 'Religious supplies', 'tag': '宗教用品', 'opalus_id': 281, },
        {'name': 'House building materials/fixtures', 'tag': '房屋建筑材料/混合物', 'opalus_id': 281, },
        {'name': 'House interior materials', 'tag': '房屋内部材料', 'opalus_id': 281, },
        {'name': 'House exterior materials', 'tag': '房屋外墙材料', 'opalus_id': 281, },
        {'name': 'House machines/fixtures', 'tag': '家用机器/混合物', 'opalus_id': 281, },
        {'name': 'Stationery and office supplies', 'tag': '文具和办公用品', 'opalus_id': 277, },
        {'name': 'Teaching materials and educational supplies', 'tag': '教学材料和教育用品', 'opalus_id': 277, },
        {'name': 'Accessories and personal items for professional use', 'tag': '专业用的配件和个人用品', 'opalus_id': 277, },
        {'name': 'Furniture for shop, office, public space', 'tag': '商店、办公室、公共空间家具', 'opalus_id': 277, },
        {'name': 'Display furniture for shop and public space', 'tag': '商店和公共空间展示家具', 'opalus_id': 277, },
        {'name': 'Equipment and facilities for public space', 'tag': '公共空间设备和设施', 'opalus_id': 277, },
        {'name': 'Equipment and facilities for professional use', 'tag': '专业使用设备和设施', 'opalus_id': 277, },
        {'name': 'Building materials and equipment for commercial space', 'tag': '商业空间建筑材料和设备', 'opalus_id': 277, },
        {'name': 'Construction/space design for industry', 'tag': '工业建筑/空间设计', 'opalus_id': 277, },
        {'name': 'Construction/space design for commercial use', 'tag': '商业用途建筑/空间设计', 'opalus_id': 277, },
        {'name': 'Air conditioning appliances', 'tag': '空调设备', 'opalus_id': 0, },
        {'name': 'House air conditioning machines/fixtures', 'tag': '家用空调机/装置', 'opalus_id': 279, },
        {'name': 'Beauty care equipment and instrument', 'tag': '美容设备和仪器', 'opalus_id': 286, },
        {'name': 'Cooking appliances', 'tag': '烹饪用具', 'opalus_id': 286, },
        {'name': 'Home appliances', 'tag': '家用电器', 'opalus_id': 286, },
        {'name': 'Toys', 'tag': '玩具', 'opalus_id': 287, },
        {'name': 'Bathroom and wet area', 'tag': '浴室和湿区', 'opalus_id': 316, },
        {'name': 'House lighting appliances', 'tag': '家用照明电器', 'opalus_id': 288, },
        {'name': 'Sporting goods', 'tag': '体育用品', 'opalus_id': 289, },
        {'name': 'Leisure/Outdoor/Travel goods', 'tag': '休闲/户外/旅游用品', 'opalus_id': 290, },
        {'name': 'Smart watch', 'tag': '智能手表', 'opalus_id': 291, }
    ]

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
        item['url'] = response.url.split('?')[0]
        # 产品名称
        title = response.xpath("//dt/span[text()='Award-winning item']/following::dd[1]//text()").extract()
        if title and title[0].strip():
            item['title'] = title[0]
            designer = response.xpath("//dt[text()='Designer']/following::dd[1]//text()").extract()
            if designer:
                item['designer'] = designer[0]
            description = response.xpath(
                "//dl[@class='detail']/dt[text()='Outline']/following::dd[1]//text()").extract()
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
            # 产品分类
            category = response.xpath("//dt/span[text()='Category']/following::dd[1]//text()").extract()
            if category:
                remark += '分类:{}\n'.format(''.join(category).strip())
                for i in self.category_list:
                    if category[0] in i['name'] or i['name'] in category[0]:
                        item['category_id'] = i['opalus_id']
                        remark += '分类标签:{}\n'.format(i['tag'])
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
                {'id': 303, 'level': level, 'time': year}, ensure_ascii=False)

            images = response.xpath('//ul[@class="thumnail"]/li//img/@src').extract()
            tmp_img = []
            if not images:
                images = response.xpath('//figure[@id="mainphoto"]//img/@src').extract()
            for image in images:
                tmp_img.append(re.sub('\?w=\d*&h=\d*', '?w=880&h=660', image))
            tmp_img = [i for i in tmp_img if 'youtube' not in i]
            item['img_urls'] = ','.join(tmp_img)
            yield item
        else:
            print(title)

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
