from scrapy.http import HtmlResponse

import requests

res = requests.get('https://opalus.d3ingo.com/')


html = HtmlResponse(url=res.url,
            body=res.content,
            request=res.request,
            # 最好根据网页的具体编码而定
            encoding='utf-8',
            status=200)
