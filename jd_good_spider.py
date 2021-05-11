# -*- coding: utf-8 -*-

import json

from design.spiders.shop.jd_good import JdSpider
from scrapy.crawler import CrawlerProcess
from design.utils.redis_operation import RedisHandle
from collections import OrderedDict

redis_cli = RedisHandle('localhost', '6379')
kwargs = {"se_port": '9222', 'time_out': 5, 'dev': False}
all_keywords = '吹风机,真无线蓝牙耳机 降噪 入耳式,果蔬干,拉杆箱,水壶,台灯,电风扇,美容器,剃须刀,电动牙刷,集成灶,衣物护理机,茶具,煮茶器,空气炸锅,按摩椅,破壁机,早餐机,酸奶机,电火锅,豆芽机,美妆冰箱,美发梳,除螨仪,筋膜枪,脱毛仪,颈椎按摩仪,扫地机器人,电动蒸汽拖把,挂烫机,烘衣机,烤箱,电饭煲,加湿器,微波炉,吸尘器,取暖器,卷/直发器,豆浆机,烤饼机,绞肉机,净水器,电压力锅,洗碗机,咖啡机,饮水机,理发器,健康秤,足浴盆,足疗机,空气净化器,除湿机,电话机,电热饭盒,电磁炉,电陶炉,油烟机,消毒柜,电热水器,燃气热水器,空气能热水器,太阳能热水器,新风机,电动滑板车,保温杯,梅子酒'
max_page = 15
# while True:
kwargs['max_page'] = max_page
fail_url = redis_cli.query('jd', 'fail_url')
page = redis_cli.query('jd', 'page')
keywords = redis_cli.query('jd', 'keywords')
price_range_list = redis_cli.query('jd', 'price_range_list')
if fail_url:
    try:
        redis_fail_url = json.loads(fail_url)
        if redis_fail_url:
            kwargs['fail_url'] = redis_fail_url
            kwargs['error_retry'] = 1
    except Exception as e:
        kwargs['key_words'] = all_keywords

elif page or keywords:
    kwargs['page'] = int(page) if page else 1
    kwargs['key_words'] = keywords
    if price_range_list:
        kwargs['price_range_list'] = json.loads(price_range_list)
else:
    kwargs['key_words'] = all_keywords
process = CrawlerProcess()
process.crawl(JdSpider, **kwargs)
process.start()