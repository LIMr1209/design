import requests

target_url = "http://httpbin.org/ip"
proxy_host = 'http-dynamic.xiaoxiangdaili.com'
proxy_port = 10030
proxy_username = '728155862681931776'
proxy_pwd = 'ih6GnOCP'

proxy_host = 'tps122.kdlapi.com'
proxy_port = 15818
proxy_username = 't11942010348139'
proxy_pwd = 'h5q66qzm'


proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxy_host,
    "port": proxy_port,
    "user": proxy_username,
    "pass": proxy_pwd,
}

proxies = {
    'http': proxyMeta,
    'https': proxyMeta,
}
for i in range(3000):
    try:
        resp = requests.get(url=target_url, proxies=proxies)
        print(resp.text)
    except Exception as e:
        print(str(e))
