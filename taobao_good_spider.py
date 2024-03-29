# -*- coding: utf-8 -*-

import json

from design.spiders.shop.taobao_new import TaobaoSpider
from scrapy.crawler import CrawlerProcess
from design.utils.redis_operation import RedisHandle

redis_cli = RedisHandle('localhost', '6379')
kwargs = {"se_port": '9666', 'time_out': 5, 'dev': False}
# while True:
fail_url = redis_cli.query('taobao', 'fail_url')
keywords = redis_cli.query('taobao', 'keywords')
# price_range_list = redis_cli.query('taobao', 'price_range_list')
if fail_url:
    try:
        redis_fail_url = json.loads(fail_url)
        if redis_fail_url:
            kwargs['fail_url'] = redis_fail_url
            kwargs['error_retry'] = 1
    except Exception as e:
        pass

elif keywords:
    kwargs['key_words_str'] = keywords
    # if price_range_list:
    #     kwargs['price_range_list'] = json.loads(price_range_list)
process = CrawlerProcess()
process.crawl(TaobaoSpider, **kwargs)
process.start()
