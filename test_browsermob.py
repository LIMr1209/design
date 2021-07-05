from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 获取network

def main():
    # 开启代理
    BMPserver = Server(r'C:\Users\aaa10\Desktop\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
    BMPserver.start()
    BMPproxy = BMPserver.create_proxy()

    # 配置代理启动webdriver
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server={}'.format(BMPproxy.proxy))
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    brosver = webdriver.Chrome(chrome_options=chrome_options)
    # 获取返回内容

    BMPproxy.new_har("my_baidu", options={'captureHeaders': True, 'captureContent': True})

    brosver.get('https://detail.tmall.com/item.htm?id=613772367738#J_Reviews')

    result = BMPproxy.har


    for rs in result['log']['entries']:
        print(rs['request']['method'], rs['request']['url'])

    brosver.get('https://baidu.com')
    result = BMPproxy.har
    print('00000000000000000000000000000000000000000000')
    for rs in result['log']['entries']:
        print(rs['request']['method'], rs['request']['url'])

main()
