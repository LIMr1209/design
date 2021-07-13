# coding:utf-8
import logging
import json
import random
import re
import time
from multiprocessing import Pool

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, ProxyError
from configparser import ConfigParser, ExtendedInterpolation
import os


def cookie_to_dict(cookie):
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}


def dict_to_cookie(data):
    cookie = ''
    for key, value in data.items():
        cookie += key + '=' + value + ';'
    cookie = cookie[:-1]
    return cookie


class CommentSpider:
    def __init__(self, tunnel_domain, tunnel_port, tunnel_user, tunnel_pwd, opalus_comment_url):
        global cf
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))  # 重试次数
        s.mount('https://', HTTPAdapter(max_retries=5))
        self.s = s
        if tunnel_domain:
            if tunnel_user:
                proxies = {
                    "http": "http://%(user)s:%(pwd)s@%(proxy)s:%(port)s/" % {"user": tunnel_user, "pwd": tunnel_pwd,
                                                                             "proxy": tunnel_domain,
                                                                             "port": tunnel_port},
                    "https": "https://%(user)s:%(pwd)s@%(proxy)s:%(port)s/" % {"user": tunnel_user, "pwd": tunnel_pwd,
                                                                               "proxy": tunnel_domain,
                                                                               "port": tunnel_port}
                }
            else:
                proxies = {
                    "http": "http://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port},
                    "https": "https://%(proxy)s:%(port)s/" % {"proxy": tunnel_domain, "port": tunnel_port}
                }
        else:
            proxies = {'http': '', 'https': ''}
        self.proxies_list = [proxies]
        self.time_out = 5
        self.sleep = False
        self.random_sleep_start = 5
        self.random_sleep_end = 10
        self.comment_tm_data_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692'
        self.taobao_comment_impression = 'https://rate.tmall.com/listTagClouds.htm?itemId=%s&isAll=true&isInner=true'
        self.comment_save_url = opalus_comment_url

    # 保存评论
    def comment_save(self, out_number, json_data, new_time):
        data = json_data['data']
        success = False
        while not success:
            try:
                res = self.s.post(self.comment_save_url, json=json_data)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(10)
                print('保存评论失败 正在重试')
                # return {'success': False, 'message': "保存失败", 'out_number': out_number}
        if res.status_code != 200 or res.json()['code']:
            message = res.json()['message']
            return {'success': False, 'message': message, 'out_number': out_number}
        # 重复爬取
        if 'existence_count' in res.json() and res.json()['existence_count'] == len(data):
            return {'success': True, 'message': '重复爬取', 'out_number': out_number}
        return {'success': True, 'message': ''}


    def data_handle(self, i):
        res = self.data_tmall_handle(i['number'], i['_id'], i['site_from'], i['new_time'])
        return res

    def data_tmall_handle(self, out_number, id, site_from, new_time):
        comment_page = 1
        while True:
            res = self.get_taobao_impression(out_number, 9)
            if res['success']:
                print("获取淘宝大家印象失败 正在重试")
                impression = res['impression']
                break
            time.sleep(5)
        # cookie_list = [
        #     {
        #         't': '7eb89f5c2e118140ef49e1f31237a35e',
        #         '_tb_token_': 'f3e5557aebd57',
        #         'cookie2': '1c695a1217e5b117d4e5225a55e7d40b',
        #         'unb': '2210910815481',
        #         'cookie17': 'UUpgRs05urYo2upivg%3D%3D',
        #     },
        # ]
        cookie_dict = cookie_to_dict(
            'xlly_s=1; cna=BlxpGa3pHwcCAXt1qFue0H25; _m_h5_tk=c5b3a9e5fcb8e7af464b740c33717bcf_1625461046485; _m_h5_tk_enc=854c2cf699871ea9dc8475e4625ae688; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; uc1=cookie21=VT5L2FSpccLuJBreK%2BBd&pas=0&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie14=Uoe2yIdH2plXgA%3D%3D; uc3=id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dCuwOxbPtD9a8VPu0%3D; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; _l_g_=Ug%3D%3D; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSUi4wEzg7hq&nk4=0%400AdtZS03tnds0llDWCRcSihqN1rrIyZSjaqW; unb=2671514723; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; cookie1=BxNSonczp%2BfH4JvkmZGiHVjnsgV7tsFybnrAAaVXt9g%3D; login=true; cookie17=UU6m3oSoOMkDcQ%3D%3D; cookie2=18a7785e1f11a1d863fcadff0362df3e; _nk_=%5Cu658C%5Cu7237%5Cu72371058169464; sgcookie=E1005zv%2Bhz6f5Q0EO2HvAzL3BmLQK8mHDiohVNhyQWporZbAdVivA6gatxv2CBF8mUelPxLo0%2FHtlfIWQt4HF3yB1g%3D%3D; sg=437; t=b471be1b6451e3223c85cf947cb281f6; csg=a23665e3; _tb_token_=3b1f30eaaee70; enc=GW3FaK%2BshiuOkvzRvsW4FqeMe6%2FMvQeuzmtgAyuMTGwNpM93PLvN7bvDd1KcdqQ88O5IlPR6AHOQnMJ7tgQBvw%3D%3D; x5sec=7b22617365727665723b32223a2239393063356638396434666539663662353835323961336132326661613663644349376569596347454f57577664376c2b5a32456d414561444449324e7a45314d5451334d6a4d374d5443756f66474e41673d3d227d; tfstk=c5DfBxAnSZbXPhAN3mtP_PyMtC2Pa0A72IarcXxLApYX_3nbysD1Ly68Ffb5eWE5.; l=eBP6SJ7Vj5lXnq8jBO5wlurza77OmIdfhsPzaNbMiInca1o5ievT1NCB06sBrdtjgt5fVetrFQx-eRUH8f4LRx_ceTwhKXIpBB96Se1..; isg=BKurbzjUTxBGJJNEY1Gj1MWGOs-VwL9CUQZQ9R0pCOpevM0epZHPkqRaFvzSnBc6')
        # cookie_dict = cookie_to_dict('sgcookie=E100nDB%2Fvt%2BlPNVUuHK1rQ5zDPLp%2F1yczzPThqqyjbUWyaB4pjon%2FguTCLdPEjihLGujJfctGXol%2FQ4fdXYRz66qmA%3D%3D; uc1=cookie14=Uoe2yIUfiLbRNA%3D%3D; t=b53111f044cc56cea4bdbd22205e0fe4; uc3=vt3=F8dCuwzn8IuXBz7Zqm0%3D&lg2=URm48syIIVrSKA%3D%3D&nk2=F5RHoWPz3gbNYt4%3D&id2=UUpgRs05urYo2upivg%3D%3D; tracknick=tb202938556; lid=tb202938556; uc4=id4=0%40U2gqyZ2h8V63RJQ0G%2BLPCwib%2Fwu8wfhL&nk4=0%40FY4Ms466dA%2FiBqQDIbngQmsGoTlKvQ%3D%3D; lgc=tb202938556; enc=V7FQMwMAHQy%2BAJxRmZYGoq5cI%2B1fCa7zdA%2FyPaANcQrnv45NgDS3JUECSPxfFuAG2E0SFNWvgg0qm0Qqi%2FmVAtQuTWf6jNAbTtED%2BAz9bfk%3D; _tb_token_=e7131e301193b; cookie2=12f5ca4f815095bfb9bd66c9c635d55b; cna=c2lgGTuTPWYCAXt1qJPODrdS; xlly_s=1; x5sec=7b22617365727665723b32223a223434626438313038326635323763316339356338393961653365393263663037434957556c596347454f5467345033463371486e65526f504d6a49784d446b784d4467784e5451344d5473784d4b366838593043227d; l=eBPOjgiljWcuu65WBO5Zhurza779eQAfCsPzaNbMiInca66ViFk3rNCBVMXWrdtjgtffdetrFQx-eR3M71adgZqhuJ1REpZZQxJM-; tfstk=crndBRtg7CAHpjet32LMPbO3lN4RaiILw9NV2pykPlQRvesRVs4ommHLIewA9lpO.; isg=BBsbP_D9_0dTLAOPhv3bgY8yqn-F8C_yQdYgpQ1awpoc7D7OlcN7QlYqhkziTIfq')
        x5sec = ''
        try:
            with open('x5sec.txt', 'r') as f:
                x5sec = f.read().strip()
        except:
            pass
        while True:
            if x5sec:
                cookie_dict['x5sec'] = x5sec
            cookie = dict_to_cookie(cookie_dict)
            proxies = random.choice(self.proxies_list)
            ua = UserAgent().random
            headers = {
                'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
                'User-Agent': ua,
                'Cookie': cookie
            }
            url = self.comment_tm_data_url % (out_number, comment_page)

            try:
                comment_res = self.s.get(url, headers=headers, verify=False, proxies=proxies, timeout=self.time_out)
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
                # x5sec = asyncio.get_event_loop().run_until_complete(get_pyppeteer_tmall_x5sec(result['url']))
                # x5sec = get_selenium_tmall_x5sec(result['url'])
                x5sec = get_file_tmall_x5sec(result['url'])
                continue
            for i in result['rateDetail']['rateList']:
                comment = {}
                comment['type'] = 1 if i['anony'] else 0
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
                json_data = {
                    'good': {'impression': impression, 'id': id, 'site_from': site_from},
                    'data': data,
                }
                # data = json.dumps(data, ensure_ascii=False)
                # res = self.comment_save(out_number, json_data, new_time)
                # if not res['success']:
                #     return res
                # if res['message'] == '重复爬取':
                #     return {'success': True, 'message': "重复爬取", 'out_number': out_number, 'id': id}
                print("保存成功天猫", comment_page, out_number, id)
            if 'paginator' not in result['rateDetail']:
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
            pages = result['rateDetail']['paginator']['lastPage']
            if comment_page >= pages:
                # self.comment_end(out_number, headers['Referer'])
                return {'success': True, 'message': "爬取成功", 'out_number': out_number, 'id': id}
            num = random.randint(self.random_sleep_start, self.random_sleep_end)
            if self.sleep:
                time.sleep(num)
            comment_page += 1

    def get_taobao_impression(self, out_number, site_from):
        proxies = random.choice(self.proxies_list)
        ua = UserAgent().random
        headers = {
            'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number if site_from == 9 else 'https://item.taobao.com/item.htm?&id=' + out_number,
            'User-Agent': ua,
            'Cookie': '_bl_uid=vjkhyfh1kL3up48m99pCr7FrpXtk; _m_h5_tk=a4901680887df4de35e80eca7db44b84_1606823592784; _m_h5_tk_enc=9bc810f0923b6d2ffa1255ef0eb10aee; t=4c621df8e85d4fe9067ccde6f510e986; cookie2=19f934d02e95023c00ef6f6c16247b20; _tb_token_=538f3e759d683; _samesite_flag_=true; xlly_s=1; enc=8VjKAvR5cUAIjOxlCLOZcKJvrc68jolYx%2B%2BXKZSjT9%2FFz8LyOvCmZRJkDd6PtDwSKarI7PYNAY8Xh0A58XSpGw%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=0_0; tracknick=; uc1=cookie14=Uoe0az6%2FCczAvQ%3D%3D; cna=zasMF12t3zoCATzCuQKpN3kO; v=0; x5sec=7b22726174656d616e616765723b32223a226536393430633233383332336665616466656166333533376635366463646233434c76446d50344645497165377565426c734f453767453d227d; l=eBjqXoucQKR1C6x3BO5aourza779rLAXhsPzaNbMiIncC6pCdopMGYxQKOsKgCtRR8XAMTLB4mWKOPytfF1gJs8X7w3xU-CtloD2B; tfstk=cyklBRcOcbP7_BVm1LwSjSvcCLyhC8Tzzvk-3xwwcEPL8GLYV75cWs5ZriK0u4DdO; isg=BC0t6dP2Dkp6levKmUHve7J9PMmnimFctAAvaW84I0aR5kOYN9gnLBbw0LoA5nkU'
        }
        try:
            impression_res = self.s.get(self.taobao_comment_impression % out_number, headers=headers, proxies=proxies,
                                        verify=False, timeout=self.time_out)
        except ProxyError as e:
            print('代理错误')
            return {'success': False, 'message': "代理错误", 'out_number': out_number}
        except requests.exceptions.RequestException as e:
            print(str(e))
            print('大家印象请求未响应')
            return {'success': False, 'message': "请求未响应", 'out_number': out_number}
        rex = re.compile('({.*})')
        try:
            impression_data = json.loads(rex.findall(impression_res.content.decode('utf-8'))[0])
        except:
            print('json load错误')
            return {'success': False, 'message': "json load错误", 'out_number': out_number}
        impression = ''
        if not "tags" in impression_data:
            print('tags 不存在 反爬')
            return {'success': False, 'message': "反爬", 'out_number': out_number}
        for i in impression_data['tags']['tagClouds']:
            impression += i['tag'] + '(' + str(i['count']) + ')  '
        return {'success': True, 'impression': impression}



def get_goods_data(category, tunnel_domain, tunnel_port, tunnel_user, tunnel_pwd,  opalus_goods_comment_url, opalus_comment_url):
    params = {'category':category , 'site_from': 9}
    page = 1
    while True:
        params['page'] = page
        success = False
        while not success:
            try:
                res = requests.get(opalus_goods_comment_url, params=params, verify=False)
                success = True
            except requests.exceptions.RequestException as e:
                time.sleep(5)
        res = json.loads(res.content)
        try:
            spider = CommentSpider(tunnel_domain, tunnel_port, tunnel_user, tunnel_pwd, opalus_comment_url)
        except Exception as e:
            print(str(e))

        for i in res['data']:
            result = spider.data_handle(i)
            print(result)
            if not result['success']:
                return result
        if not res['data']:
            break
        page += 1
    return {'success': True, 'message': ''}


# 手动滑块获取cookie 保存文件
def get_file_tmall_x5sec(url):
    print(url)
    time.sleep(10)
    x5sec = ''
    try:
        with open('x5sec.txt', 'r') as f:
            x5sec = f.read().strip()
    except:
        pass
    return x5sec

def func(msg):
    print("in:", msg)
    print("out,", msg)

if __name__ == '__main__':
    import urllib3

    urllib3.disable_warnings()
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    basedir = os.path.abspath(os.path.dirname(__file__))

    cf = ConfigParser(interpolation=ExtendedInterpolation())
    filename = os.path.abspath(os.path.join(basedir, "..", '..', '..', ".env"))
    cf.read(filename, encoding="utf-8")

    tunnel_domain = cf.get('proxies', 'tunnel_domain', fallback='')
    tunnel_port = cf.get('proxies', 'tunnel_port', fallback='')
    tunnel_user = cf.get('proxies', 'tunnel_user', fallback='')
    tunnel_pwd = cf.get('proxies', 'tunnel_pwd', fallback='')
    opalus_comment_url = cf.get('api', 'opalus_comment_url', fallback='')
    opalus_goods_comment_url = cf.get('api', 'opalus_goods_comment_url', fallback='')

    caty_list = ['烤箱', '电饭煲', '加湿器']
    pool = Pool(3)  # 创建拥有10个进程数量的进程池
    for i in caty_list:
        pool.apply_async(get_goods_data, (i, tunnel_domain, tunnel_port, tunnel_user, tunnel_pwd,  opalus_goods_comment_url, opalus_comment_url))
    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()

