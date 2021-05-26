import random
import string
import zipfile

import scrapy
from scrapy.utils.project import get_project_settings
from pydispatch import dispatcher
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from scrapy import signals
from fake_useragent import UserAgent


def create_proxyauth_extension(tunnelhost, tunnelport, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件

    args:
        tunnelhost (str): 你的代理地址或者域名（str类型）
        tunnelport (int): 代理端口号（int类型）
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=tunnelhost,
        port=tunnelport,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


class SeleniumSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        self.mySetting = get_project_settings()
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 无头浏览器
        # 这些网站识别不出来你是用了Selenium，因此需要将模拟浏览器设置为开发者模式
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        # 不加载图片
        # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # if self.mySetting['TUNNEL_USER']:
        #     # 有密码
        #     proxyauth_plugin_path = create_proxyauth_extension(
        #         tunnelhost=self.mySetting['TUNNEL_DOMAIN'],  # 隧道域名
        #         tunnelport=self.mySetting['TUNNEL_PORT'],  # 端口号
        #         proxy_username=self.mySetting['TUNNEL_USER'],  # 用户名
        #         proxy_password=self.mySetting['TUNNEL_PWD']  # 密码
        #     )
        #     chrome_options.add_extension(proxyauth_plugin_path)
        # else:
        #     # ip 无密码
        #     chrome_options.add_argument(
        #         "--proxy-server=http://{}:{}".format(self.mySetting['TUNNEL_DOMAIN'], self.mySetting['TUNNEL_PORT']))
        # ua
        # ua = UserAgent().random
        # chrome_options.add_argument("user-agent={}".format(ua))
        #
        # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenium\AutomationProfile"
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:{}".format(kwargs['se_port']))
        # 其中PageLoadStrategy有三种选择： 默认normal
        # (1) NONE: 当html下载完成之后，不等待解析完成，selenium会直接返回
        # (2) EAGER: 要等待整个dom树加载完成，即DOMContentLoaded这个事件完成，仅对html的内容进行下载解析
        # (3) NORMAL: 即正常情况下，selenium会等待整个界面加载完成（指对html和子资源的下载与解析,如JS文件，图片等，不包括ajax）
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "normal"  # complete
        # caps["pageLoadStrategy"] = "eager"  #interactive
        # caps["pageLoadStrategy"] = "none"
        # 初始化chrome对象
        self.browser = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)

        # self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #           Object.defineProperty(navigator, 'webdriver', {
        #             get: () => undefined
        #           })
        #         """
        # })
        # self.browser.maximize_window()
        # if self.windowHeight and self.windowWidth:
        #     self.browser.set_window_size(900, 900)
        self.browser.set_page_load_timeout(kwargs['time_out'])  # 页面加载超时时间
        self.browser.set_script_timeout(kwargs['time_out']) # 执行js 超时时间
        self.wait = WebDriverWait(self.browser, 30)  # 指定元素加载超时时间
        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        # dispatcher.connect(receiver=self.mySpiderCloseHandle,
        #                    signal=signals.spider_closed
        #                    )
        # super(SeleniumSpider, self).__init__(*args, **kwargs)

    def mySpiderCloseHandle(self, spider):
        pass
        # self.browser.quit()
