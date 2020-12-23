# 德国iF设计奖

import scrapy
import json
from design.items import DesignItem
from lxml import etree
import re, requests, csv, os, random, redis
import hashlib


class RedDotSpider(scrapy.spiders.Spider):
    name = "ifward"
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
    url = 'https://ifworlddesignguide.com/api/v2/articles/design_excellence?cursor=%s&lang=en&count=30&orderby=date&filter={"filters":[{"type":"awards","ids":[1]}]}&time_min=%s&time_max=%s'

    # url = 'https://ifworlddesignguide.com/api/v2/articles/design_excellence?cursor=60&lang=en&count=30&orderby=date&filter={"filters":[{"type":"awards","ids":[1]},{"type":"gold_awarded","ids":[1]}]}&time_min=%s&time_max=%s'

    def start_requests(self):
        for i in range(2015, 2021):
            year = str(i)
            yield scrapy.Request(self.url % (0, year, year), callback=self.body_response, meta={'year': year})
        # yield scrapy.Request(self.url % (0, 1954, 1954), callback=self.body_response, meta={'year': 1954})

    def body_response(self, response):
        year = response.meta['year']
        body = json.loads(response.text)
        for data in body['data']:
            url = data['href']
            if data['type'] == 'goldaward':
                prize = {
                    'id': 297,
                    'time': str(year),
                    'level': 'GOLD AWARDED/金奖'
                }
            else:
                prize = {
                    'id': 297,
                    'time': str(year),
                    'level': 'iF DESIGN AWARD/iF设计奖'
                }
            item = DesignItem()
            item['title'] = data['headline']
            item['description'] = data['description']
            item['url'] = url
            item['evt'] = 3
            item['channel'] = 'iF Design Award'
            yield scrapy.Request(url, callback=self.item_deal, meta={'item': item, 'prize': prize})
        if body['meta']['next_cursor']:
            next_cursor = body['meta']['next_cursor']
            yield scrapy.Request(self.url % (next_cursor, year, year), callback=self.body_response,meta={'year': year})

    def item_deal(self, response):
        item = response.meta['item']
        prize = response.meta['prize']
        statement = response.xpath("//div[@class='text-quote-wrapper']/div[1]/text()").extract()
        if statement:
            statement = statement[0]
        else:
            statement = ''
        prize['statement'] = statement
        item['prize'] = json.dumps(prize, ensure_ascii=False)
        item['tags'] = ','.join(response.xpath("//span[@itemprop='alternateName']/text()").extract())
        # 备注
        remark_list = response.xpath("//div[@class='profile-text-box-wrapper']/ul/li").extract()
        remark = ''
        if remark_list:
            for remark_item in remark_list:
                html = etree.HTML(remark_item)
                if html.xpath('//span/text()')[0] == 'DATE OF LAUNCH':
                    remark = remark + '发布时间:{}\n'.format(html.xpath('//span/text()')[1])
                elif html.xpath('//span/text()')[0] == 'DEVELOPMENT TIME':
                    remark = remark + '开发周期:{}\n'.format(html.xpath('//span/text()')[1])
                elif html.xpath('//span/text()')[0] == 'TARGET REGIONS':
                    remark = remark + '目标区域:{}\n'.format(html.xpath('//span/text()')[1])
                elif html.xpath('//span/text()')[0] == 'TARGET GROUPS':
                    remark = remark + '目标群体:{}\n'.format(html.xpath('//span/text()')[1])
        item['remark'] = remark
        # 设计师，品牌，生产者
        item['company'] = ''
        div_box = response.xpath("//div[@class='column large-4 product-client-box']").extract()
        if div_box:
            for div_item in div_box:
                div = etree.HTML(div_item)
                i = div.xpath('//span/text()')
                if not i:
                    continue
                if i[0] == 'University':
                    design = div.xpath('//div[@class="product-client-box-content"]/p/text()')
                    university = div.xpath('//div[@class="product-client-box-content"]/h2/text()')[0]
                    designer = [d.strip() if d.strip() != university else '' for d in design]
                    designer = [d for d in designer if d != '']
                    item['designer'] = ','.join(designer)
                elif i[0] == 'Client / Manufacturer':
                    company = div.xpath('//div[@class="product-client-box-content"]/p/text()')
                    item['customer'] = ','.join([c.strip() for c in company if c != ''])
                elif i[0] == 'Design':
                    design = div.xpath('//div[@class="product-client-box-content"]/p/text()')
                    tmp_list = [c.strip() for c in design if c != '']
                    item['designer'] = tmp_list[len(tmp_list) - 1]
                    company_href = div.xpath('//a[@class="arrow-button"]/@href')
                    if company_href:
                        item['company'] = self.get_company(company_href[0])
                    if item['company'] == '':
                        item['company'] = div.xpath('//div[@class="product-client-box-content"]/h2/text()')[0]
        # images = response.xpath("//img[@alt='{}']/@data-src".format(item['title'])).extract()
        images = response.xpath('//div[contains(@class,"product-image")]//img/@data-src').extract()
        img_urls = []
        for i in images:
            if not 'youtube' in i:
                img_urls.append(i)
        item['img_urls'] = ','.join(img_urls)
        # print(item)
        yield item

    def get_company(self, href):
        item = [None] * 6
        url = 'https://ifworlddesignguide.com{}'.format(href)
        item[0] = url
        req = requests.get(url)
        if req.status_code != 200:
            return ''
        html = etree.HTML(req.text)
        company_name = html.xpath("//div[@class='column small-10 header-headlines']/h2/text()")[0]
        item[1] = company_name
        red = redis.Redis(host='localhost', port=6379, db=1)
        m = hashlib.md5()
        b = company_name.encode(encoding='utf-8')
        m.update(b)
        key = 'CSV:' + m.hexdigest()
        if red.get(key):
            return company_name
        good_at = html.xpath('//table/tbody/tr')
        be_good_at = ''
        for good_item in good_at:
            goods = good_item.xpath('//td/text()')
            be_good_at = be_good_at + ','.join([good for good in goods if good != '\xa0']) + '||'
        item[5] = be_good_at
        contact_data = html.xpath('//div[@class="contact-data"]/p/text()')
        for contact_item in contact_data:
            if 'Phone' in contact_item.strip():
                item[2] = contact_item.strip()
        if item[2] == None:
            item[2] = ''
        company_url = html.xpath('//div[@class="contact-data"]/p/a/text()')
        for c in company_url:
            if 'http' in c:
                item[4] = c
            if '@' in c:
                item[3] = c
        if item[3] == None:
            item[3] = ''
        if item[4] == None:
            item[4] = ''
        title = ['信息来源地址', '公司名称', '联系电话', '公司邮箱', '公司网站', 'iF奖获得情况']
        filename = './0company_info.csv'
        if os.path.exists(filename):
            with open(filename, 'a', newline='', encoding='gb18030') as fw:
                wr = csv.writer(fw)
                wr.writerow(item)
                fw.close()
        else:
            with open(filename, 'a', newline='', encoding='gb18030') as fw:
                wr = csv.writer(fw)
                wr.writerow(title)
                wr.writerow(item)
                fw.close()
        print('保存信息成功')
        return company_name