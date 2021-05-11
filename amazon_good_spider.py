# -*- coding: utf-8 -*-

import json

from design.spiders.shop.amazon_good import AmazonGoodSpider
from scrapy.crawler import CrawlerProcess
from design.utils.redis_operation import RedisHandle

redis_cli = RedisHandle('localhost', '6379')
kwargs = {"se_port": '9222', 'time_out': 5, 'dev': False}
all_keywords = [
    # {'name': '烤饼机', 'value':'electric baking pan'},
    {'name': '空气炸锅', 'value':'AirFryer'},
]
# max_page = 15
# while True:
# kwargs['max_page'] = max_page
fail_url = redis_cli.query('amazon', 'fail_url')
keywords = redis_cli.query('amazon', 'keywords')
if fail_url:
    try:
        redis_fail_url = json.loads(fail_url)
        if redis_fail_url:
            kwargs['fail_url'] = redis_fail_url
            kwargs['error_retry'] = 1
    except Exception as e:
        kwargs['key_words'] = all_keywords

elif keywords:
    kwargs['key_words'] = json.loads(keywords)
else:
    kwargs['key_words'] = all_keywords
process = CrawlerProcess()
process.crawl(AmazonGoodSpider, **kwargs)
process.start()