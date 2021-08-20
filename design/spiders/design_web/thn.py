import scrapy
import json


class DesignCaseSpider(scrapy.Spider):
    name = 'thn'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.taihuoniao.com']
    fail_url = []
    page_url = 'https://www.taihuoniao.com/api/product/list?page=%s&per_page=24'
    detail_url = 'https://www.taihuoniao.com/product/view?id=%s'

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': True,  # 启用cookie
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.UserAgentSpiderMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    def start_requests(self):
        yield scrapy.Request(self.page_url % (1), meta={'page': 1}, callback=self.parse_list)

    def parse_list(self, response):
        page = response.meta['page']
        data = json.loads(response.text)  # getall() 返回多个 get() 返回单个
        for i in data['data']:
            yield scrapy.Request(self.detail_url%i['_id'], callback=self.parse_detail)
        if page < 10:
            page += 1
            yield scrapy.Request(url=self.page_url % (page), callback=self.parse_list,
                                 meta={'page': page})

    def parse_detail(self, response):
        print(response.request.headers)
        print(response.headers)
