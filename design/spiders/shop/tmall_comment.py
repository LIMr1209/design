import json
import re
import time
import datetime
import requests
import scrapy
from fake_useragent import UserAgent
from pydispatch import dispatcher
from requests.adapters import HTTPAdapter
from scrapy import signals
from scrapy.utils.project import get_project_settings
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from design.spiders.selenium import SeleniumSpider
from design.utils.redis_operation import RedisHandle
import asyncio
import random
from pyppeteer import connect

# chrome.exe --remote-debugging-port=9666 --user-data-dir="C:\selenium_copy_12\AutomationProfile"


class TmallCommentSpider(SeleniumSpider):
    name = "tmall_comment"
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'DOWNLOADER_MIDDLEWARES': {
            'design.middlewares.SeleniumMiddleware': 543,
        },
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'log/%s.log' % name
    }

    def __init__(self, *args, **kwargs):
        self.page = 1
        self.redis_cli = RedisHandle('localhost', '6379')
        self.list_url = []
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.setting = get_project_settings()
        self.opalus_goods_comment_url = self.setting['OPALUS_GOODS_COMMENT_URL']
        self.comment_save_url = self.setting['OPALUS_COMMENT_URL']

        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'


        super(TmallCommentSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(receiver=self.except_close,
                           signal=signals.spider_closed
                           )
        old_num = len(self.browser.window_handles)
        js = 'window.open("https://www.taobao.com/");'
        self.browser.execute_script(js)
        self.browser.switch_to_window(self.browser.window_handles[old_num])  # 切换新窗口


    def except_close(self):
        pass

    # 滑块破解
    async def pyppeteer_code(self):
            connect_params = {
                'browserWSEndpoint': 'ws://127.0.0.1:9222/devtools/browser/b85d9d9e-da29-474e-8e31-7f235447cfe0',
                'logLevel': 3,
            }
            browser = await connect(connect_params)
            page = await browser.newPage()
            # await page.setExtraHTTPHeaders({'Proxy-Authorization': 'Basic ' + ('{"H56R2946P953B99D"}:{"8ADE908B093EFBB9"}').toString('base64')})
            # await page.setExtraHTTPHeaders({'Proxy-Authorization': 'Basic ' + proxyUser + ':' + proxyPass.toString('base64')})
            await page.setViewport({'width': 1366, 'height': 768})
            await page.setUserAgent(
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
            await page.evaluate('''() =>{Object.defineProperties(navigator,{webdriver:{get: () => false}})}''')
            await page.evaluateOnNewDocument(
                '() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            await page.goto('https:' + url, {'timeout': 1000 * 50})
            await asyncio.sleep(1)
            try:
                # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
                await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
            except:
                return 1, page
            try:
                await page.mouse.down()
                steps = random.randint(58, 80)
                print("steps:{}".format(steps))
                await page.mouse.move(2000, 0, {'steps': 120})
                await page.mouse.up()
            except Exception as e:
                print('{}:验证失败'.format(e))

                return None, page
            else:
                # 判断是否通过
                slider_again = await page.querySelector('.nc_iconfont.icon_warn')
                if slider_again != None:
                    print("验证失败")
                    return None, page
                else:
                    # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
                    print('验证通过')
                    return 1, page

    def browser_get(self, url):
        try:
            self.browser.get(url)
        except TimeoutException as e:
            self.browser_get(url)
        except WebDriverException as e:
            try:
                self.browser.execute_script('window.stop()')
            except Exception as e:
                pass
            self.browser_get(url)

    def start_requests(self):
        self.list_url = self.get_list_urls()  # 获取商品链接
        yield scrapy.Request(self.list_url[0]['url']+'#J_Reviews', callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True})

    def get_list_urls(self):
        params = {}
        params['reverse'] = 0
        params['site_from'] = 9
        params['category'] = ''
        params['page'] = self.page
        success = False
        while not success:
            try:
                res = requests.get(self.opalus_goods_comment_url, params=params, verify=False)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
        res = json.loads(res.content)
        list_url = res['data']
        self.page += 1
        return list_url


    def parse_detail(self, response):
        self.comment_page_get()
        self.list_url.pop(0)
        if not self.list_url:
            self.page += 1
            self.list_url = self.get_list_urls()
        yield scrapy.Request(self.list_url[0]['url']+'#J_Reviews', callback=self.parse_detail, dont_filter=True,
                             meta={'usedSelenium': True})

    # 保存评论
    def comment_save(self, out_number, data):
        success = False
        while not success:
            try:
                res = self.s.post(self.comment_save_url, json=data)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
                # return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            print(message, out_number)
            self.comment_save(out_number, data)
        # 重复爬取
        if 'existence_count' in res.json() and res.json()['existence_count'] == len(data):
            print('重复爬取', out_number)


    def comment_page_get(self):
        try:
            elem = WebDriverWait(self.browser, 10, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="rate-sort "]')
                )
            )
        except:
            self.browser.refresh()
            time.sleep(2)
            self.comment_page_get()
        element_to_hover_over = self.browser.find_element_by_xpath('//div[@class="rate-sort "]')
        hover = ActionChains(self.browser).move_to_element(element_to_hover_over)  # 找到元素
        hover.perform()  # 悬停
        try:
            elem = WebDriverWait(self.browser, 10, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//li[@event-val="sort_1"]')
                )
            )
        except:
            self.browser.refresh()
            time.sleep(2)
            self.comment_page_get()
        self.browser.find_element_by_xpath('//li[@event-val="sort_1"]').click() # 时间排序
        while True:
            time.sleep(2)
            res = self.get_comment()
            try:
                next_ele = self.browser.find_element_by_xpath('//span[@class="rate-page-break"]/following-sibling::a[1]')
                next_ele.click()
            except:
                break



    def get_comment(self):
        data = []
        out_number = self.list_url[0]['number']
        impression = self.get_impression(out_number)
        comment_trs = self.browser.find_elements_by_xpath('//div[@class="rate-grid"]//tr')
        for i in comment_trs:
            comment = {}
            buyer = i.find_element_by_xpath('.//div[@class="rate-user-info"]').get_attribute('innerText').strip().replace("（匿名）",'')
            style_ele = i.find_elements_by_xpath('.//div[@class="rate-sku"]/p')
            style = []
            for j in style_ele:
                style.append(j.get_attribute('innerText'))
            style = ';'.join(style)
            try:
                i.find_element_by_xpath('.//div[@class="tm-rate-append"]')
                append = True
            except:
                append = False
            if append:
                date = i.find_element_by_xpath('.//div[@class="tm-rate-premiere"]//div[@class="tm-rate-date"]').get_attribute('innerText').strip()
            else:
                date = i.find_element_by_xpath('.//td[@class="tm-col-master"]/div[@class="tm-rate-date"]').get_attribute('innerText').strip()
            add = ''
            if append:
                first = i.find_element_by_xpath('.//div[@class="tm-rate-premiere"]//div[@class="tm-rate-fulltxt"]').get_attribute('innerText').strip()
                add = i.find_element_by_xpath('.//div[@class="tm-rate-append"]//div[@class="tm-rate-fulltxt"]').get_attribute('innerText').strip()
            else:
                first = i.find_element_by_xpath('.//div[@class="tm-rate-content"]/div[@class="tm-rate-fulltxt"]').get_attribute('innerText').strip()
            if first == '此用户没有填写评论!':
                comment['first'] = ''
            else:
                comment['first'] = first
            if append:
                image_ele = i.find_elements_by_xpath('.//div[@class="tm-rate-premiere"]/div[@class="tm-rate-content"]//ul[@class="tm-m-photos-thumb"]/li')
            else:
                image_ele = i.find_elements_by_xpath('.//td[@class="tm-col-master"]/div[@class="tm-rate-content"]//ul[@class="tm-m-photos-thumb"]/li')
            images = []
            for j in image_ele:
                images.append('https:'+j.get_attribute('data-src').replace('_400x400.jpg', ''))
            if date == '今天':
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                date = datetime.datetime.strptime('2021.'+ date, '%Y.%m.%d').strftime('%Y-%m-%d %H:%M:%S')

            comment['images'] = ','.join(images)
            comment['add'] = add
            comment['impression'] = impression
            comment['good_url'] = self.list_url[0]['url']
            comment['date'] = date
            comment['style'] = style
            comment['buyer'] = buyer
            comment['site_from'] = 9
            data.append(comment)
        if data:
            self.comment_save(out_number, data)
            print("保存成功天猫", self.page, out_number)

    # 大家印象
    def get_impression(self, out_number):
        impression = ''
        try:
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
                'User-Agent': ua,
                'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
            }
            try:
                impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers,
                                            verify=False, timeout=10)
            except:
                time.sleep(5)
                impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers,
                                            verify=False, timeout=10)
            rex = re.compile('({.*})')
            impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
            for i in impression_data['tags']['tagClouds']:
                impression += i['tag'] + '(' + str(i['count']) + ')  '
        except:
            pass
        return impression

