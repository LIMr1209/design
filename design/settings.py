# -*- coding: utf-8 -*-

# Scrapy settings for Meizitu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'design'

SPIDER_MODULES = ['design.spiders']
NEWSPIDER_MODULE = 'design.spiders'

# RETRY_ENABLED = True # 开启重试

# RETRY_TIMES = 3 # 重试次数

# Obey robots.txt rules
ROBOTSTXT_OBEY = False # 不遵循爬虫协议
# HTTPERROR_ALLOWED_CODES = [404]


# LOG_LEVEL = 'ERROR'  # 日志级别
#
LOG_FILE = 'log/ERROR.log' # 默认日志文件
# Configure maximum concurrent requests performed by Scrapy (default: 16)
# Scrapy下载器将执行的最大并发（即并发）请求数。
CONCURRENT_REQUESTS = 16  # 并发请求数
# 在项目管道中并行处理的最大并发项目数（每个响应）
CONCURRENT_ITEMS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0  # 下载延迟
# The download delay setting will honor only one of:

# CONCURRENT_REQUESTS_PER_DOMAIN 是每个域的并发请求数量 默认是8 设置了该参数应该会更有效的防止爬虫被屏蔽。还有一个参数CONCURRENT_REQUESTS_PER_IP 他是作用到每个IP上，并不是作用到域了。
# CONCURRENT_REQUESTS_PER_DOMAIN = 16  # 多线程
# CONCURRENT_REQUESTS_PER_IP = 16 # 多线程

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

"""
1.COOKIES_ENABLED = True 时：

   1. scrapy 启动 CookiesMiddleware 中间件，为请求自动添加服务器响应的 cookie，

   2. 如果我们在 Request 中，使用 cookies 参数添加 cookie 时， 我们添加的 cookie 会额外加入到请求头中，如果响应有重名设置，则覆盖。（即，cookies 参数的cookie优先，但是 response 里的 cookie 也一个不少）

   3. 如果我们使用 headers 参数添加 cookie，headers添加的 cookie 会失效，被响应 cookie 完全覆盖。（即，headers里设置的 cookie 无效）

2.COOKIES_ENABLED = False 时：

   1. scrapy 关闭 CookiesMiddleware 中间件，response 设置的 cookie 失效

   2. 使用 cookies 设置的 cookie 失效。

   3. 使用 headers 设置的 cookie 保留。
"""

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers: 默认请求头
# DEFAULT_REQUEST_HEADERS = {
#     'Host': 'www.laisj.com',
#     'Cache-Control': 'no-cache',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Cookie': '_ga=GA1.2.22582115.1550218744; UM_distinctid=16e0097668d672-06d0dc86e10d94-3f75065b-384000-16e0097668eda2; PHPSESSID=3miirajgr13jnr45qm5usp18ju; acw_tc=7cc1f43915749089317778318ef68d7776dabc9d0d1d17dabc7cef58e4; _gid=GA1.2.1547875979.1574908934; Hm_lvt_c84c6dfaf119e270700a348f9073b2c2=1574911593; nb-referrer-hostname=www.laisj.com; acw_sc__v2=5ddf68832875692d58da0dc507055a7c9464cb5d; CNZZDATA1260548842=1992531904-1564021327-%7C1574921790; Hm_lpvt_c84c6dfaf119e270700a348f9073b2c2=1574922376; pt_4099d0b9=uid=5-J56HCwMc51rmVOUekcEw&nid=0&vid=k93b6mDbh7BBthqI2Cex8g&vn=8&pvn=1&sact=1574922376224&to_flag=0&pl=q9SDdT17dY4Tn6z1CPIOwA*pt*1574922376224; pt_s_4099d0b9=vt=1574922376224&cad=; nb-start-page-url=http%3A%2F%2Fwww.laisj.com%2Fcasestudy%2F11655.html',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
# }
# IMAGES_STORE = "./Images"

# Enable or disable spider middlewares  爬虫中间件
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'design.middlewares.DesignSpiderMiddleware': 543,

}

# Configure item pipelines  管道
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'design.pipelines.ImagePipeline': 301,
    'design.pipelines.ImageSavePipeline': 301,

}

# Enable or disable downloader middlewares  下载中间件
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'design.middlewares.DesignDownloaderMiddleware': 543,
    'design.middlewares.UserAgentSpiderMiddleware': 300,
    # 'design.middlewares.ProxySpiderMiddleware': 543,
    # 'design.middlewares.SeleniumMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

PROXY_LIST = [
    '127.0.0.1:1080'
]
# 自动限制爬行速度。
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True  # 开启缓存  默认 False
# 缓存策略 默认 DummyPolicy 不考虑服务器返回的HTTP Cache-Control指示，它会缓存所有的请求和响应。
# RFC2616Policy 这种缓存策略会考虑服务器返回的缓存指令，大概类似于浏览器的行为
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.DummyPolicy'
# HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'
# 缓存文件存储 默认 FilesystemCacheStorage,  DBM存储 DbmCacheStorage
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'
HTTPCACHE_EXPIRATION_SECS = 0  # 有效时长 0 不过期  秒为单位
HTTPCACHE_DIR = 'httpcache' # 存储HTTP 缓存的目录。 默认httpcache  如果为空，HTTP 缓存将被禁用
# HTTPCACHE_IGNORE_HTTP_CODES = []  # 忽略缓存指定状态码得请求
# HTTPCACHE_GZIP = False # 压缩格式

# 爬虫允许的最大深度，可以通过meta查看当前深度；0表示无深度
DEPTH_LIMIT = 0

# 爬取时，0表示深度优先Lifo(默认)；1表示广度优先FiFo
# 后进先出，深度优先
DEPTH_PRIORITY = 0
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleLifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.LifoMemoryQueue'

# 先进先出，广度优先
# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# 配置mongodb相关配置
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017

# 数据库名称
MONGODB_DBNAME = "opalus"
SHEETE_NAME = "produce-item"

SELENIUM_TIMEOUT = 25  # selenium浏览器的超时时间，单位秒
LOAD_IMAGE = False  # 是否下载图片
WINDOW_HEIGHT = 900  # 浏览器窗口大小
WINDOW_WIDTH = 900

# configparser 自定义配置信息

from configparser import ConfigParser, ExtendedInterpolation
import os

basedir = os.path.abspath(os.path.dirname(__file__))

cf = ConfigParser(interpolation=ExtendedInterpolation())
cf.read(os.path.abspath(os.path.join(basedir, "..", ".env")), encoding='utf-8')
# api接口
OPALUS_GOODS_URL = cf.get('api', 'opalus_goods_url')
OPALUS_COMMENT_URL = cf.get('api', 'opalus_comment_url')
OPALUS_GOODS_COMMENT_URL = cf.get('api', 'opalus_goods_comment_url')
PRODUCT_SAVE_URL = cf.get('api', 'product_save_url')
OPALUS_GOODS_CATEGORY_URL = cf.get('api', 'opalus_goods_category_url')
OPALUS_GOODS_LIST_URL = cf.get('api', 'opalus_goods_list_url')
OPALUS_GOODS_REMOVE_URL = cf.get('api', 'opalus_goods_remove_url')
IMG_SAVE_PATH = cf.get('img', 'save_path')
# 隧道代理
TUNNEL_DOMAIN = cf.get('proxies', 'tunnel_domain')
TUNNEL_PORT = cf.get('proxies', 'tunnel_port')
TUNNEL_USER = cf.get('proxies', 'tunnel_user')
TUNNEL_PWD = cf.get('proxies', 'tunnel_pwd')
# 拼多多用户鉴权
PDD_ACCESS_TOKEN_LIST = cf.get('pdd_user', 'access_token_list').split('\n')
PDD_VERIFY_AUTH_TOKEN = cf.get('pdd_user', 'verify_auth_token').split('\n')
# 拼多多用户鉴权
JD_ACCOUNT_LIST = cf.get('jd_user', 'account_list').split('\n')
JD_PASSWORD_LIST = cf.get('jd_user', 'password_list').split('\n')
