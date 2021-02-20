from scrapy import cmdline
import argparse
from scrapy.crawler import CrawlerProcess

parser = argparse.ArgumentParser()
parser.add_argument("-spider", "--spider", type=str, required=True, help="爬虫脚本name")
parser.add_argument("-is_shop", "--is_shop", default=True, type=bool, required=False, help="是否是电商爬虫, 默认是")
args = parser.parse_args()
if args.is_shop:
    # 电商爬虫
    parser.add_argument('-key_words', type=str, required=False, help="爬取关键词 ','分隔",
                        default='理发器,健康秤,足浴盆,足疗机,空气净化器,除湿机,电话机,电热饭盒, 电磁炉, 电陶炉, 油烟机, 消毒柜,电热水器,燃气热水器,空气能热水器, 太阳能热水器,新风机')
    parser.add_argument('-dev', default=False, type=bool, required=False, help="是否是正式, 默认非正式")
    parser.add_argument('-max_page', default=15, type=int, required=False, help="爬取最大页码,默认15")  # 不足15页按照实际页码数量
    parser.add_argument('-time_out', default=20, type=int, required=False, help="selenium页面加载超时时间")  # 不足15页按照实际页码数量
    parser.add_argument('-se_port', default='9333', type=str, required=False, help="selenium启动端口")
    args = parser.parse_args()
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
    cmdline.execute('scrapy crawl {}'.format(args['spider']).split())

"['吹风机', '真无线蓝牙耳机 降噪 入耳式', '果蔬干', '拉杆箱', '水壶', '台灯', '电风扇', '美容器', '剃须刀', '电动牙刷', '集成灶', '衣物护理机']"
"""
['空气炸锅', '按摩椅', '破壁机', '早餐机', '酸奶机', '电火锅', '豆芽机', '美妆冰箱', '美发梳', '除螨仪', '筋膜枪', '脱毛仪, '
 '颈椎按摩仪','扫地机器人', '电动蒸汽拖把', '挂烫机', '烘衣机', '烤箱', '电饭煲', '加湿器', '微波炉', '吸尘器', '取暖器', '卷/直发器', '豆浆机', '烤饼机',
 '绞肉机','净水器','电压力锅','洗碗机']
"""
'''
['咖啡机','养生壶', '饮水机', '理发器', '健康秤', '足浴盆', '足疗机', '空气净化器', '除湿机', '电话机', '电热饭盒', '电磁炉', '电陶炉', '油烟机', '消毒柜', '电热水器', '燃气热水器', '空气能热水器', '太阳能热水器','新风机']
'''
'''
[
        U盘,
        VR眼镜,
        主板,
        交换机,
        保温杯,
        保险柜,
        儿童座椅,
        充电宝,
        内存条,
        冰箱,
        净水器,
        加湿器,
        台式机主机,
        吸尘器,
        垃圾桶,
        平板电脑,
        平衡车,
        录音笔,
        微波炉,
        手机,
        手柄,
        手环,
        手表,
        打印机,
        扫地机器人,
        扫描枪,
        投影仪,
        摩托车,
        显卡,
        智能锁,
        智能马桶,
        望远镜,
        洗衣机,
        滑板,
        激光笔,
        烟雾报警器,
        热水器,
        理发器,
        电动螺丝刀,
        电暖器,
        电烤箱,
        电视,
        相机,
        眼镜,
        硬盘,
        空气净化器,
        空调,
        笔记本散热器,
        笔记本电脑,
        网卡,
        网络机顶盒,
        行车记录仪,
        跑步机,
        路由器,
        车载充电器,
        车载空气净化器,
        转椅,
        键盘,
        音箱,
        麦克风,
        鼠标,
    ]
'''
