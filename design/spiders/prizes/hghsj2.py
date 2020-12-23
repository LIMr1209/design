# 韩国好设计奖 最新
from copy import copy
import scrapy
import copy
from design.items import DesignItem
from design.spiders.selenium import SeleniumSpider
import json, time
import datetime

datetime.timedelta()


class HghsjSpider(scrapy.Spider):
    name = "hghsj2"
    allowed_domains = ["award.kidp.or.kr"]

    custom_settings = {
        # 'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            'design.middlewares.SeleniumMiddleware': 543,
            # 'design.middlewares.UserAgentSpiderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    url = 'https://award.kidp.or.kr/Exhibit/selectHistorySearchList.json'

    data = {
        'cd_gubun1': '1',
        'cd_gubun2': '2',
        'cd_gubun3': '3',
        'chk3_1': '1',
        'chk3_2': '2',
        'chk3_3': '3',
        'chk3_4': '4',
        'chk3_5': '5',
        'chk3_6': '6',
        'searchTitle': '',
        'cdGubunList': '1, 2, 3',
        'awardsCate1List': '1, 2, 3, 4, 5, 6',
        'exhibitCate1List': '',
        'cdAreaList': '',
        'rows': '20',
    }

    def start_requests(self):
        for i in range(2020, 2021):
            data = copy.deepcopy(self.data)
            data['year'] = str(i)
            data['page'] = str(1)
            yield scrapy.FormRequest(
                url=self.url,
                formdata=data,
                callback=self.parse,
                meta={'page': 1, 'year': i}
            )

    def parse(self, response):
        res = json.loads(response.text)
        for i in res['rows']:
            item = DesignItem()
            prize = {
                'time': str(i['year_info']),
                'level': i['tp_prize_nm'] + ' Prize' if i['tp_prize_nm'] else '' ,
                'id': 304,
            }
            item['prize'] = json.dumps(prize, ensure_ascii=False)
            item['title'] = i['exhibit_title']
            item['description'] = i['exhibit_description']
            item['evt'] = 3
            item['channel'] = "hghsj"
            item['company'] = i['usernm'] if i['usernm'] else ''
            item['url'] = 'https://award.kidp.or.kr/Exhibit/index_gd_view.do?idx_exhibit=' + str(i['idx_exhibit'])
            img_host = 'https://award.kidp.or.kr/file/thumbnail.do?img_physical='
            img_urls = []
            if i['img_physical_main']:
                img_urls.append(img_host + i['img_physical_main'])
            if i['img_physical_sub1']:
                img_urls.append(img_host + i['img_physical_sub1'])
            if i['img_physical_sub2']:
                img_urls.append(img_host + i['img_physical_sub2'])
            if i['img_physical_sub3']:
                img_urls.append(img_host + i['img_physical_sub3'])
            if i['img_physical_sub4']:
                img_urls.append(img_host + i['img_physical_sub4'])
            item['img_urls'] = ','.join(img_urls)
            yield item
        page = response.meta['page']
        year = response.meta['year']
        if page < res['total']:
            page += 1
            data = copy.deepcopy(self.data)
            data['year'] = str(year)
            data['page'] = str(page)
            yield scrapy.FormRequest(
                url=self.url,
                formdata=data,
                callback=self.parse,
                meta={'page': page, 'year': year}
            )
