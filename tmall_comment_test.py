import asyncio
import json
import random
import re
import time
import requests
from fake_useragent import UserAgent
from pyppeteer import connect
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError


async def mouse_slide(url):
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
    await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    await page.goto('https:'+url, {'timeout': 1000 * 50})
    await asyncio.sleep(1)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
    except:return 1, page
    try:
        await page.mouse.down()
        steps = random.randint(58, 80)
        print("steps:{}".format(steps))
        await page.mouse.move(2000, 0, {'steps':120})
        await page.mouse.up()
    except Exception as e:
        print('{}:验证失败'.format(e))

        return None, page
    else:
        # 判断是否通过
        slider_again = await page.querySelector('.nc_iconfont.icon_warn')
        if slider_again!=None:
            print("验证失败")
            return None, page
        else:
            # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
            print('验证通过')
            return 1, page

def cookie_to_dic(cookie):
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}


def dict_to_cookie(data):
    cookie = ''
    for key, value in data.items():
        cookie += key + '=' + value + ';'
    cookie = cookie[:-1]
    return cookie


comment_tm_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=3&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692&ua=%s'
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=5))  # 重试次数
s.mount('https://', HTTPAdapter(max_retries=5))


def data_tmall_handle(out_number):
    comment_page = 1
    while True:
        # cookie_dict = {
        #     't': '7eb89f5c2e118140ef49e1f31237a35e',
        #     '_tb_token_': 'f3e5557aebd57',
        #     'cookie2': '1c695a1217e5b117d4e5225a55e7d40b',
        #     'unb': '2210910815481',
        #     'cookie17': 'UUpgRs05urYo2upivg%3D%3D',
        #     'x5sec': '7b22617365727665723b32223a226663626539653930306135313966663261633637626238386634373765613939434a4749316f5947454b4339332b4c632b6f62556e774561447a49794d5441354d5441344d5455304f4445374d5443756f66474e41673d3d227d',
        # }
        cookie_dict = {
            'x5sec': '7b22617365727665723b32223a22333964313166323866346161623434386362333737643163336130356365376443495743316f594745506d586a63756e324b4b2f6e674561444449324e7a45314d5451334d6a4d374e436941424443756f66474e41673d3d227d',
            'unb': '2671514723',
            'cookie17': 'UU6m3oSoOMkDcQ%3D%3D',
            'cookie2': '14afef918099fa1af5cef3074ead2ec3',
            't': '0906303aa9a7f271161bb03f51f721cd',
            '_tb_token_': 'eeee3b3750ed',
        }
        ua_params = '098#E1hv19vRvpWvUvCkvvvvvjiWPFFZtjEhn2SZgj1VPmPO1jiRRFqy0j3PPFFv6jDURvhvCvvvvvmvvpvZ7D6Ckjqw7Dif27s5PEt4PHiMz1V+vpvEvvABmlxxCWuMRvhvCvvvvvvRvpvhvv2MMQvCvvOvUvvvphvUvpCWvWDivvwTD7zhz8TrEcqh1jxlHdUf8+BlYE7rejvrdExr1EAKfvDr1WCl53hkLOkQD70OVC69D7zhQ8TxO94U+8c6+ul1pccG1Rp4Vd9Cvm9vvvvvphvvvvvv99CvpvvPvvmmvhCvmhWvvUUvphvUA9vv99CvpvF8uvhvmvvv926Cd+JRkvhvC99vvOCto8OCvvpvvUmm39hvCvvhvvm+vpvEvvQh9rNcChUwdvhvmpvWjvrX7po//9=='
        cookie = dict_to_cookie(cookie_dict)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
            'User-Agent': ua,
            'Cookie': cookie
        }
        url = comment_tm_data_url % (out_number, comment_page, ua_params)

        try:
            comment_res = s.get(url, headers=headers, verify=False, timeout=5)
        except ProxyError as e:
            print('代理错误')
            time.sleep(5)
            continue
            # return {'success': False, 'message': "代理错误", 'out_number': out_number, 'page': comment_page}
        except requests.exceptions.RequestException as e:
            print('请求未响应')
            time.sleep(5)
            continue
            # return {'success': False, 'message': "反爬限制", 'out_number': out_number, 'page': comment_page}
        rex = re.compile('({.*})')
        try:
            result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
        except:
            print('json load 错误')
            time.sleep(5)
            continue
        data = []
        if not 'rateDetail' in result or not result['rateDetail']:
            print('反爬限制')
            if 'url' in result:
                asyncio.get_event_loop().run_until_complete(mouse_slide(result['url']))
            time.sleep(10)
            continue
        for i in result['rateDetail']['rateList']:
            comment = {}
            comment['type'] = 1 if i['anony'] else 0
            comment['good_url'] = headers['Referer']
            comment['site_from'] = 9
            images = []
            if 'pics' in i:
                for j in i['pics']:
                    images.append('https:' + j)
            comment['images'] = ','.join(images)
            if i['rateContent'] == '此用户没有填写评论!':
                comment['first'] = ''
            else:
                comment['first'] = i['rateContent']
            comment['add'] = i['appendComment']['content'] if i['appendComment'] else ''
            comment['buyer'] = i['displayUserNick']
            comment['style'] = i['auctionSku']
            comment['date'] = i['rateDate']
            data.append(comment)
        if data:
            print("保存成功天猫", comment_page, out_number)
        pages = result['rateDetail']['paginator']['lastPage']
        if comment_page >= pages:
            # self.comment_end(out_number, headers['Referer'])
            return {'success': True, 'message': "爬取成功", 'out_number': out_number}
        time.sleep(6)
        comment_page += 1


import urllib3

urllib3.disable_warnings()
data_tmall_handle('521518690010')
data_tmall_handle('584740907378')
data_tmall_handle('603188362608')
data_tmall_handle('596096249743')
data_tmall_handle('564702949506')
data_tmall_handle('574695877355')
data_tmall_handle('547510287578')

