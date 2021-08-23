# -*- coding: utf-8 -*-

import json

from design.spiders.shop.jd_good import JdSpider
from scrapy.crawler import CrawlerProcess
from design.utils.redis_operation import RedisHandle

redis_cli = RedisHandle('localhost', '6379')
kwargs = {"se_port": '9222', 'time_out': 5, 'dev': False}
# while True:
fail_url = redis_cli.query('jd', 'fail_url')
page = redis_cli.query('jd', 'page')
keywords = redis_cli.query('jd', 'keywords')
# price_range_list = redis_cli.query('jd', 'price_range_list')
if fail_url:
    try:
        redis_fail_url = json.loads(fail_url)
        if redis_fail_url:
            kwargs['fail_url'] = redis_fail_url
            kwargs['error_retry'] = 1
    except:
        pass

elif page and keywords:
    kwargs['page'] = int(page) if page else 1
    kwargs['key_words_str'] = keywords
    # if price_range_list:
    #     kwargs['price_range_list'] = json.loads(price_range_list)
process = CrawlerProcess()
process.crawl(JdSpider, **kwargs)
process.start()
