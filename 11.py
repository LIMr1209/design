# -*- coding: utf-8 -*-

from design.spiders.shop.tmall_comment import TmallCommentSpider
from scrapy.crawler import CrawlerProcess
from design.utils.redis_operation import RedisHandle

redis_cli = RedisHandle('localhost', '6379')
kwargs = {"se_port": '9222', 'time_out': 10, 'dev': False}
process = CrawlerProcess()
process.crawl(TmallCommentSpider, **kwargs)
process.start()
