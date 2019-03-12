# Gadget Flow

import scrapy
import re
from design.items import CompanyItem
import requests
from lxml import etree


class WebsiteSpider(scrapy.spiders.Spider):
    name = "website_a"
    allowed_domains = ["shop.99114.com"]
    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.ProxySpiderMiddleware': 301,
        }

    }

    def start_requests(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        url = "http://shop.99114.com/list/pinyin/%s_%d"
        words = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # for i in range(0,26):
        word = "E"
        get_page_url = url % (word, 9999)
        html = etree.HTML(requests.get(get_page_url).text)
        name_list = html.xpath('//div[@id="page"]/div[@class="page_list"]/span[@class="current"]/text()')
        total_page = int(name_list[0]) + 1
        for page in range(1, total_page):
            print(page)
            # to_url = url % (word , page)
            # yield scrapy.Request(to_url, callback=self.body_response , headers=headers,meta={'page':page})
            # break
            # break

    def body_response(self, response):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        page = response.meta['page']
        urls = response.xpath('//div[@id="footerTop"]/descendant::a/@href').extract()
        for url in urls:
            yield scrapy.Request(url + '/ch2', callback=self.item_page, headers=headers, meta={'page': page})
            # yield scrapy.Request('http://shop.99114.com/42973296/ch2', callback=self.item_page ,headers=headers)
            # break

    def item_page(self, response):
        page = response.meta['page']
        print('第%d页' % page)
        item = CompanyItem()
        item['name'] = response.xpath('//a[@id="signtitle"]/text()').extract()[0].strip().replace('\n', '')
        item['soure_url'] = response.url
        item['craw_user_id'] = 7
        item['channel'] = 'shop99114'
        tmp_arr = response.xpath('//div[@class="sj-line sjDiv2"]/p/span[1]/text()').extract()
        i = 0
        for tmp_str in tmp_arr:
            i += 1
            if tmp_str.strip().replace('\n', '')[0:4] == '经营模式':
                management_model = response.xpath(
                    '//div[@class="sj-line sjDiv2"]/p[' + str(i) + ']/span[2]/text()').extract()
                if management_model:
                    if management_model[0].strip().replace('\n', '') != '暂未填写':
                        item['management_model'] = management_model[0].strip().replace('\n', '')
                    else:
                        item['management_model'] = ''

            elif tmp_str.strip().replace('\n', '')[0:4] == '主营业务':
                scope_business = response.xpath('//div[@class="sj-line sjDiv2"]/p[' + str(i) + ']/span[2]').extract()
                if scope_business:
                    if scope_business[0].strip().replace('\n', '') != '暂未填写':
                        pat = re.compile('(?<=\>).*?(?=\<)')
                        pat.findall(scope_business[0])
                        item['scope_business'] = ''.join(pat.findall(scope_business[0]))
                    else:
                        item['scope_business'] = ''

            elif tmp_str.strip().replace('\n', '')[0:4] == '所在地区':
                address = response.xpath('//div[@class="sj-line sjDiv2"]/p[' + str(i) + ']/span[2]/text()').extract()
                if address:
                    if address[0].strip().replace('\n', '') != '暂未填写':
                        item['province'] = address[0].strip().replace('\n', '').split(' ')[0]
                        item['city'] = address[0].strip().replace('\n', '').split(' ')[1]

        s_contact_name = response.xpath('//li[@class="picContact clearfix"]/div/p[1]/span/text()').extract()
        if s_contact_name:
            if s_contact_name[0] != '暂未填写':
                item['s_contact_name'] = s_contact_name[0]

        s_sex = response.xpath('//li[@class="picContact clearfix"]/div/p[1]/text()').extract()
        if s_sex:
            if s_sex[0].strip().replace('\n', '') == '先生':
                item['s_sex'] = 1
            else:
                item['s_sex'] = 2
        else:
            item['s_sex'] = 0

        s_contact_phone = response.xpath('//span[@class="phoneNumber"]/text()').extract()
        if s_contact_phone:
            if s_contact_phone[0].strip().replace('\n', '') != '暂未填写':
                item['s_contact_phone'] = s_contact_phone[0].strip().replace('\n', '')

        s_contact_qq = response.xpath('//a[@class="qq_img ml5 mt3"]/@title').re(r'联系(\d*)')
        if s_contact_qq:
            item['s_contact_qq'] = s_contact_qq[0]

        s_contact_wx = response.xpath('//div[@class="addIntroR"]/img/@src').extract()
        if s_contact_wx:
            item['s_contact_wx'] = 'http://shop.99114.com' + s_contact_wx[0]

        s_contact_email = response.xpath('//li[@class="addIntro clearfix"]/span[@class="addR"]/text()').extract()
        if s_contact_email:
            if s_contact_email[0].strip().replace('\n', '') != '暂未填写':
                item['s_contact_email'] = s_contact_email[0].strip().replace('\n', '')

        s_tel = response.xpath('//li[@class="addIntro clearfix"]/span[@class="addR telephoneShow"]/text()').extract()
        if s_tel:
            if s_tel[0].strip().replace('\n', '') != '暂未填写':
                item['s_tel'] = s_tel[0].strip().replace('\n', '')

        address = response.xpath('//span[@id="detialAddr"]/text()').extract()
        if address:
            if address[0].strip().replace('\n', '') != '暂未填写':
                item['address'] = address[0].strip().replace('\n', '')

        info_arrs = response.xpath(
            '//div[@class="widget company_detail  "]/descendant::ul[@class="m-comul m-comulR clearfix"]/descendant::p/span[@class="c-span"]/text()').extract()
        j = 0
        for info_str in info_arrs:
            j += 1
            if info_str.strip().replace('\n', '')[0:4] == '员工数量':
                scale_label = response.xpath(
                    '//div[@class="widget company_detail  "]/descendant::ul[@class="m-comul m-comulR clearfix"]/descendant::div[@class="companytxt"]/p[' + str(
                        j) + ']/span[@class="c-span2"]/text()').extract()
                if scale_label:
                    if scale_label[0] != '暂未填写':
                        item['scale_label'] = scale_label[0]
        item['edit_pattern'] = 0
        # print(item)
        yield item
