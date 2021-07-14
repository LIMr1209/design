import json
import re
import urllib
from urllib import parse
import time
import requests
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_slide_url():
    cookie = 'xlly_s=1; cna=BlxpGa3pHwcCAXt1qFue0H25; _m_h5_tk=c5b3a9e5fcb8e7af464b740c33717bcf_1625461046485; _m_h5_tk_enc=854c2cf699871ea9dc8475e4625ae688; dnk=%5Cu658C%5Cu7237%5Cu72371058169464; uc1=cookie21=VT5L2FSpccLuJBreK%2BBd&pas=0&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie14=Uoe2yIdH2plXgA%3D%3D; uc3=id2=UU6m3oSoOMkDcQ%3D%3D&nk2=0rawKUoBrqUrgaRu025xgA%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dCuwOxbPtD9a8VPu0%3D; tracknick=%5Cu658C%5Cu7237%5Cu72371058169464; lid=%E6%96%8C%E7%88%B7%E7%88%B71058169464; _l_g_=Ug%3D%3D; uc4=id4=0%40U2xrc8rNMJFuLuqj%2FSUi4wEzg7hq&nk4=0%400AdtZS03tnds0llDWCRcSihqN1rrIyZSjaqW; unb=2671514723; lgc=%5Cu658C%5Cu7237%5Cu72371058169464; cookie1=BxNSonczp%2BfH4JvkmZGiHVjnsgV7tsFybnrAAaVXt9g%3D; login=true; cookie17=UU6m3oSoOMkDcQ%3D%3D; cookie2=18a7785e1f11a1d863fcadff0362df3e; _nk_=%5Cu658C%5Cu7237%5Cu72371058169464; sgcookie=E1005zv%2Bhz6f5Q0EO2HvAzL3BmLQK8mHDiohVNhyQWporZbAdVivA6gatxv2CBF8mUelPxLo0%2FHtlfIWQt4HF3yB1g%3D%3D; sg=437; t=b471be1b6451e3223c85cf947cb281f6; csg=a23665e3; _tb_token_=3b1f30eaaee70; enc=GW3FaK%2BshiuOkvzRvsW4FqeMe6%2FMvQeuzmtgAyuMTGwNpM93PLvN7bvDd1KcdqQ88O5IlPR6AHOQnMJ7tgQBvw%3D%3D; x5sec=7b22617365727665723b32223a2239393063356638396434666539663662353835323961336132326661613663644349376569596347454f57577664376c2b5a32456d414561444449324e7a45314d5451334d6a4d374d5443756f66474e41673d3d227d; tfstk=c5DfBxAnSZbXPhAN3mtP_PyMtC2Pa0A72IarcXxLApYX_3nbysD1Ly68Ffb5eWE5.; l=eBP6SJ7Vj5lXnq8jBO5wlurza77OmIdfhsPzaNbMiInca1o5ievT1NCB06sBrdtjgt5fVetrFQx-eRUH8f4LRx_ceTwhKXIpBB96Se1..; isg=BKurbzjUTxBGJJNEY1Gj1MWGOs-VwL9CUQZQ9R0pCOpevM0epZHPkqRaFvzSnBc6'
    ua = UserAgent().random
    out_number = '644440364707'
    headers = {
        'Referer': 'https://detail.tmall.com/item.htm?id=%s' % out_number,
        'User-Agent': ua,
        'Cookie': cookie
    }
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=972811287&sellerId=2901218787&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&groupId=&needFold=0&_ksTS=1606704651028_691&callback=jsonp692' % (
    out_number, 1)
    comment_res = requests.get(url, headers=headers, verify=False, timeout=5)
    rex = re.compile('({.*})')
    result = json.loads(rex.findall(comment_res.content.decode('utf-8'))[0])
    return 'https:' + result['url']


def get_x5sec_api(url):
    url = url.replace(':443', '')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 初始化chrome对象
    browser = webdriver.Chrome(options=chrome_options)
    while True:
        try:
            browser.get(url)
            break
        except:
            pass
    time.sleep(1)
    cookie = ''
    cookies = browser.get_cookies()
    for i in cookies:
        cookie += i['name'] + '=' + i['value'] + ';'
    cookie = cookie[:-1]

    slidedata_n_list = [
        # '140#tVXopJAezzP5Hzo24xmT4pN8s7a59FoRvsubBo4E+YLDuWBbA2NNp6g4Gtl4VejBrRKwI3FkD8/qlbzxgG2K5PzizznOv1kvlpTzzPzbVXlqlbrx7y0+I3EtzHOb2XU+l1Xx+QZ/9SvZrI7Zb6eV/u4yy5GH2hMA9451A32ZTB+LkFzdCoG2zxXhhwOQTMI3exw/9Kjn4E2dK0ChGQb4WqqkAvdM9bn+ymcx4SCQg3JHyxRMSc3Rc1EWZV1uQp6mO3qKQq+v/wCnowTCGsZAsPC7ZFDfz6ziFVFpHGI+R3rtulcn4wpeOVbtFw62smZhtQPG65JEIr+DEViY4PosWIL/HVjBmk4gEVPsa0PcT/jO/myO4lazzeL+zL1WOvn7hQL8EGRdr2TZb2XDjGV93fzawhWwN75NRl9BAso3LgcMfJ9t0BeEgykLMTXNvVqwrZM7t5q3z62StTiNVuCvxxb3hxqEMRg5xqrf0Lj9QGRDdZOWZJ4OcIUPmNHYQ1NW8ruRbgbUaMCXce/Uc0Tpb1PCCC98bbQmnoy4O1ZewBbPFJyGq14ET3Mn3oRbEri/JH8Kf/SwmYiajhhV4ezU5XS/aJ06hkHWXq40Hgi6RY4URcvH0kOgIlSLx/qxytH1SRa10s63E+Tx+i6sbjinDVaUBB9Xh6JO5/e2YTZBqkatFjhFzN0lwqEli0DAoU1IN2KQwhVi3GpVZLgez1sIYOVQ4hlFlWAx9/S7OjQrsAoivRymRti24JcN3qwElwEgV0g9ucU6usrjGdDH9Gm0SyrwuasZsIc/8EtefGHWziA4A5QYIXqYV935wflwP7U3F1HJ4fBWL6DyFenjfB1uyBO2tgLwug/CDhbjbtCmANCQipMVmcCodBIIr+pF7jda/D85hvdtzgNB55C1cSSAFYIzJ+lG8ONVXmx0PjIo6gtCc96J7tiQNr/Z/MwxxfpPAzpCwfewlK7sR1WbLl+jj9dDy5OVaeQ4bzfnolyYrZnx1XT=',
        # '140#2Muo0IyZzzPZTQo24ZzQ4pN8s7a59P02upUHHT9JDR8R+b8ayKXCAFjYzzL5Wps0cWGfI0L94bSnlp1zz/kPro+3ozzx0xwd7th/zzrb22U3lp1xzjydV2VulFDa2Dc3V3gvzZarhaLLMZ2aMX4tqgAQLSJ9OI6QTUsA5TCm5ykykXKgA7mTCmQGP+sGdXRhoIXlwPrqFv1uJrtl/5RROYZs968VzWL+HB7IpzyjQL8iXyDrf9A3j2mAWDQEJHJWlTBF8Kt4Wv1XVGNQ3ola+7n41RWa8uTE3qxIpSFSNiZ1gwQAgD9b4Z/Y/gMINlsw4bem2314kG0ZWv6+cKlw2cdh1tok6BIrx8TB9Hux4ERwatz3KI8gSIOXIbLv+KTeFD9Bp3jYJcGvkiqO+82kD6LxFqjnpYsm2YgW+ccJ29iTz0ZWpvF8ARw0y5CDChSmsUTsfTWZsq1xve1RwwF7dOryci3cTkbjmR2N177oIG42Z50okoj7ZtbBAgXjB8UoiLttqvHDozsuKfkVinARNxLDkCyhbg4QlFuM30o+PdkT72GZkZXJac97JN+gfoBdIZkakBlJ193i1kX7knevOgRSjuaBYVkmqFSdEWI7rbrzA+tSb7HECpK9GaDA+yDIdxWVfjgvnSut6Tt9p/IeVoCUkkxP9ss+H5zrBnb8bwp2rb8prjX1KT7QhfPSwrIM4MGuicl/Hz1TwNlWmgv1baixNuMjKCso7MuytWHQRsEfVtBE/cjWuCy9rBoyO45gUPL/P4npzJ6auZtx3eSaSqFUQWMIGmGR1gVTuRbvVaF+qwqa5O0libbYHmWuQBweL9SHKdGyUVTFnsGFtAm7UG4YTaF9CXopoxKhS3GQFhrsKXKu7i8EPnLtgJZymuVUfoGe6xpnhIIyr4GHAV2wLTDyiVV5HKKuTQ4+8TREbIcsRsu52RmnFo1kk/j0f8ddbU5A1u/reTFZLA5XbGsO8DQ0Dzkq4KezGcVE'
        '140#n9+oYdTZzzPt4zo24Z2Q4pN8s7a59XUJ0JncwXnhMrWewhnDrjeUKoEhkKb+FH+mlx3JyVj94bVmlp1zz/kPdMAFfFzxKH82O3h/zzrb22U3lp1xzFfOV2VulFDa2Dc3V3g3zZR38YLLMZ2aMX4tX6DmzxnfzKmmMAcR6NIWJrtuvaMn+oGeVj7be1Vw7GpxI8OIG3lxZ9CRly39EoDb8soeysLLHcAi5w0LMP4GaryXGlrdvZZeicK1A34oTaF+EKgz0ibcKkn0Q2z6MphYgGu2OOieAglnceQAIXA/3IDjJB/vgRvgbJal36KzvFLN51TeFD9Bp3jYJcGvqy0Y1+YmlUhXBAGwfU+h9LA0gxW95akiSjYozO0DdSvlnzAVIIRfDu/TfTWK0T+6QsqpXrAqdIao/BQBSCndNnMvl0euX5UbQrBTXu/UE7orw50WZahKy72AwMG/yvg8REiZc0g15wSl0jIvmZ5YP+7LYIQW4q25TCzUH/oFUSBl/d2gFeaXFRsXtzrUCFDtEqUjtrOx44IDoHA6t0BU1kzzI79r3W9p2TIAmv1uYocPmyFxT8jxfC7XVImE2OgbCJGEEyFUGj4q0lErI2izckXPBuRvJUE24ynXUPcRHi2iHJ1PJYZmRHA4PY8vsKyek9gerpel3DvcSNdZmvXISFUCVoga9+XBvvdQDH2cTMlORQh9TZAQITHRwQKRhLvu9Gzn/TIHOpGHQSeEr00xirQLN7iprFUikzXH6so7z1wHMreytqEDB59idn00zUeBKoBojxHh/rqeygpd2BFnHp54TyYtXk1sflrgfvTjf8JRs1uOteSmfZiX2NDFMt92Wccn1yqf3SDwb2zYgozi6VniSrGJmYoEQhJTUmgrMx+DkURIqqeusG/LvS6eQtI8Lkio/7UFUXBlvKnFCTDP43nRnYecjjf+2LKJhF=='
    ]

    rex = re.compile('window._config_ = ({.*?})', re.DOTALL)
    data = json.loads(rex.findall(browser.page_source)[0])
    t = data['NCTOKENSTR']
    a = data['NCAPPKEY']
    n = random.choice(slidedata_n_list)

    slidedata = {
        "a": a,
        "t": t,
        "n": n,
        "p": "{\"ncSessionID\":\"5e701f050179\",\"umidToken\":\"T2gA2FQ_TPyArkB9nSjaYB9KjuePyX9NJgxLR33V1Ceknt51DzeHhh80XWWa4XuroZI=\"}",
        "scene": "register",
        "asyn": 0,
        "lang": "cn",
        "v": 1039
    }
    slidedata = urllib.parse.quote(json.dumps(slidedata))

    x5secdata = data['SECDATA']

    try:
        slide_url = 'https://rate.tmall.com/list_detail_rate.htm/_____tmd_____/slide?slidedata=%s&x5secdata=%s&v=05935722416069973'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Cookie': cookie,
            'referer': url
        }

        request_url = slide_url % (slidedata, x5secdata)

        response = requests.get(request_url, headers=headers)
        if 'Set-Cookie' not in response.headers:
            return {'success': False, 'message': '破解失败'}
        else:
            x5sec_cookie = response.headers.get('Set-Cookie')
            x5sec_cookie_list = x5sec_cookie.split(';')
            x5sec = x5sec_cookie_list[0].split('=')[1]
            return {'success': True, 'message': 'success', 'data': x5sec}
    except Exception as e:
        return {'success': False, 'message': '程序错误 ' + str(e)}


if __name__ == '__main__':
    url = get_slide_url()
    print(get_x5sec_api(url))
