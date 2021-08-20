import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.linkextractors import LinkExtractor
from pydispatch import dispatcher
from scrapy import signals, Selector
from scrapy.loader import ItemLoader

from design.items import DesignItem
# scrapy 信号相关库
from design.spiders.selenium import SeleniumSpider
import datetime

data = {
    'channel': 'yankodesign',
    'evt': 3,
}


# Field 字段事实上有两个参数：
# 第一个是输入处理器（input_processor） ，当这个item，title这个字段的值传过来时，可以在传进来的值上面做一些预处理。
# 第二个是输出处理器（output_processor） ， 当这个item，title这个字段被预处理完之后，输出前最后的一步处理。

# 第一步， 通过 add_xpath(), add_css() 或者 add_value() 方法)，提取到数据。
# 第二步，将提取到的数据，传递到输入处理器（input_processor）中进行处理，处理结果被收集起来，并且保存在ItemLoader内（但尚未分配给该Item）。
# 第三步，最后调用输出处理器（output_processor）来处理之前收集到的数据（这是最后一步对数据的处理）。然后再存入到Item中，输出处理器的结果是被分配到Item的最终值｡
# 第四步，收集到所有的数据后, 调用ItemLoader.load_item() 方法来填充，并得到填充后的 Item 对象。

class CustomItemLoader(ItemLoader):
    # 提取的数据，填充进去的对象都是List类型。而我们大部分的需求是要取第一个数值，取List中的第一个非空元素
    default_output_processor = TakeFirst()  # 输出 列表得第一个元素
    tags_out = Join(',')
    description_out = Join('\n')


class DesignCaseSpider(SeleniumSpider):
    name = 'yankodesign'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.yankodesign.com']
    date_threshold = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y/%m/%d')
    category_list = ['productdesign', 'technology', 'automotive']
    fail_url = []
    cate_url = 'https://www.yankodesign.com/category/%s/'
    page_url = 'https://www.yankodesign.com/category/%s/page/%s/'

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # 启用cookie
        'DOWNLOADER_MIDDLEWARES': {
            # 代理中间件
            # 'design.middlewares.ProxiesMiddleware': 400,
            # SeleniumMiddleware 中间件
            'design.middlewares.UserAgentSpiderMiddleware': 400,
            'design.middlewares.SeleniumMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'design.pipelines.ImagePipeline': 301,
        }
    }

    def __init__(self, *args, **kwargs):

        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        super(DesignCaseSpider, self).__init__(*args, **kwargs)

    def except_close(self):
        print(self.fail_url)

    def start_requests(self):
        # fail_url = []
        # for i in fail_url:
        #     yield scrapy.Request(i, callback=self.parse_detail)
        # yield scrapy.Request(
        #     'https://www.yankodesign.com/2021/08/18/nissan-reveals-the-2023-z-model-fitting-it-out-with-a-turbocharged-engine-and-400-hp-for-the-smoothest-ride-yet/',
        #     callback=self.parse_detail)
        for i in self.category_list:
            yield scrapy.Request(self.cate_url % (i), meta={'page': 1, 'category':i}, callback=self.parse_list)

    def parse_list(self, response):
        page = response.meta['page']
        category = response.meta['category']
        # link = LinkExtractor(restrict_xpaths='//article/figure/a')
        # detail_list = link.extract_links(response)
        # for i in detail_list:
        #     print(i.url)
        detail_list = response.xpath('//article/figure/a/@href').getall()  # getall() 返回多个 get() 返回单个
        if not detail_list:
            print(response.url)
        # yield scrapy.Request(detail_list[0], callback=self.parse_detail, meta={'usedSelenium': True})
        next_page = True
        date_re = re.compile(r'\d+/\d+/\d+')
        for i in detail_list:
            if match := date_re.search(i):
                if match.group() < self.date_threshold:
                    next_page = False
                    continue
            yield scrapy.Request(i, callback=self.parse_detail)
        # max_page = response.xpath('//a[@class="page-numbers"][last()]/text()').extract()[0].replace(',', '')
        # if page < int(max_page) and continue_count < len(detail_list):
        if next_page:
            page += 1
            yield scrapy.Request(url=self.page_url % (category, page), callback=self.parse_list,
                                 meta={'page': page, 'category': category})

    def parse_detail(self, response):
        item = CustomItemLoader(item=DesignItem(), response=response)
        item.add_value('url', response.url)
        try:
            img_urls = response.xpath('//div[contains(@class, "single-box clearfix entry-content")]').re(
                r'<noscript><img.*?src="(.*?)".*?</noscript>')
            for i in range(len(img_urls)):
                # if not img_urls[i].startswith('https://www.yankodesign.com'):
                #     img_urls[i] = 'https://www.yankodesign.com' + img_urls[i]
                img_urls[i] = img_urls[i].replace("amp;", '').replace("#038;", "")
            if not img_urls:
                try:
                    img_urls = response.xpath(
                        '//img[contains(@class,"alignnone size-full") or contains(@class, "aligncenter size-full")]/@src').getall()
                except:
                    img_urls = response.xpath('//img[@class="postpic"]/@src').getall()
            designer = response.xpath('string(//div[@class="grid-8 column-1"]/div/p[contains(text(),"Designer:") or contains(text(), "Designers:")])').get().strip()
            item.add_value('img_urls', ','.join(img_urls))
            if designer:
                item.add_value('designer', designer.split(':')[1].strip())
            item.add_xpath('title', '//h1[@class="entry-title"]/text()')

            desc_list_p = response.xpath('//div[@class="grid-8 column-1"]/div[1]/p')
            desc_text_list = []
            for i in desc_list_p:
                desc = i.xpath('string(.)').get()
                if desc:
                    b = re.search("Designer[s]*:[\s\S]*", desc)
                    if b:
                        continue
                    desc_text_list.append(desc)
            item.add_xpath('tags', '//div[@class="single-box tag-box clearfix"]/a/text()')
            if desc_text_list:
                item.add_value('description', desc_text_list)
            for key, value in data.items():
                item.add_value(key, value)
        except Exception as e:
            print(str(e), response.url)
            self.fail_url.append(response.url)
        yield item.load_item()
