from scrapy import cmdline
import argparse
from scrapy.crawler import CrawlerProcess

parser = argparse.ArgumentParser()
parser.add_argument("-spider", "--spider", type=str, required=True, help="爬虫脚本name")
parser.add_argument("-is_shop", "--is_shop", action='store_true', help="是否是电商爬虫, 默认是")
# 电商爬虫
parser.add_argument('-key_words', type=str, required=False, help="爬取关键词 ','分隔",
                    default='除螨仪,筋膜枪,脱毛仪,颈椎按摩仪,扫地机器人,电动蒸汽拖把,挂烫机,烘衣机,烤箱,电饭煲,加湿器,微波炉,吸尘器,取暖器,卷/直发器,豆浆机,烤饼机,绞肉机,净水器,电压力锅,洗碗机')
parser.add_argument('-dev', default=False, type=bool, required=False, help="是否是正式, 默认非正式")
parser.add_argument('-max_page', default=15, type=int, required=False, help="爬取最大页码,默认15")  # 不足15页按照实际页码数量
parser.add_argument('-time_out', default=10, type=int, required=False, help="selenium页面加载超时时间")  # 不足15页按照实际页码数量
parser.add_argument('-se_port', default='9222', type=str, required=False, help="selenium启动端口")
args = parser.parse_args()
if args.is_shop:
    kwargs = vars(args)
    process = CrawlerProcess()  # 括号中可以添加参数
    if args.spider == 'taobao':
        from design.spiders.shop.taobao_new import TaobaoSpider

        process.crawl(TaobaoSpider, **kwargs)
    if args.spider == 'jd':
        from design.spiders.shop.jd_good import JdSpider

        process.crawl(JdSpider, **kwargs)
    if args.spider == 'pdd':
        from design.spiders.shop.pinduoduo import PddSpider

        process.crawl(PddSpider, **kwargs)
    process.start()
else:
    # 普通爬虫
    cmdline.execute('scrapy crawl {}'.format(args.spider).split())
