from scrapy import cmdline
# cmdline.execute('scrapy crawl taobao_list -a key_words="吹风机"'.split()) #
cmdline.execute('scrapy crawl taobao -a key_words=集成灶'.split())

'''
水壶（6207） 台灯（9898） 电风扇（751） 耳机（842） 美容器（795）
 电吹风（740） 剃须刀（739） 电动牙刷（741） 电水壶/热水瓶（760）  拉杆箱（2589）
'''
