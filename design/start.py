from scrapy import cmdline
# cmdline.execute('scrapy crawl taobao_list -a key_words="吹风机"'.split()) #
cmdline.execute('scrapy crawl jdsj-new -a key_words=吹风机'.split())
# cmdline.execute('scrapy crawl taobao_test -a key_words=吹风机'.split())
