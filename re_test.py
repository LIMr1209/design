import re

# a = '<noscript>&lt;img class="alignnone size-full wp-image-283133" src="https://www.yankodesign.com/images/design_news/2020/10/RGKitPlay_a_motion_control_kit.jpg" alt="" width="1050" <noscript>&lt;img class="alignnone size-full wp-image-283133" src="https://www.yankodesign.com/images/design_news/2020/10/RGKitPlay_a_motion_control_kit.jpg" alt="" width="1050"</noscript><noscript>&lt;img class="alignnone size-full wp-image-283133" src="https://www.yankodesign.com/images/design_news/2020/10/RGKitPlay_a_motion_control_kit.jpg" alt="" width="1050" <noscript>&lt;img class="alignnone size-full wp-image-283133" src="https://www.yankodesign.com/images/design_news/2020/10/RGKitPlay_a_motion_control_kit.jpg" alt="" width="1050"</noscript>'
# a = '<noscript>&lt;img src="https://static.wixstatic.com/media/2635bf_27afca1a1124404ebf1fefce5db51e45~mv2.gif/v1/fill/w_800,h_450/Pluuus-Power%20Bank.gif" alt="" width="1050" height="590" data-jpibfi-post-excerpt="" data-jpibfi-post-url="https://www.yankodesign.com/2019/09/10/the-pluuus-is-the-next-generation-of-wallets-designed-for-life-in-2020/" data-jpibfi-post-title="The Pluuus is the next generation of wallets designed for life in 2020" data-jpibfi-src="https://static.wixstatic.com/media/2635bf_27afca1a1124404ebf1fefce5db51e45~mv2.gif/v1/fill/w_800,h_450/Pluuus-Power%20Bank.gif" ></noscript>'
# a = '<noscript>&lt;img src="https://www.yankodesign.com/images/design_news/2020/10/auto-draft/chipolo_ocean_2.jpg" alt="" width="1050" height="700" class="aligncenter size-full wp-image-282902" data-jpibfi-post-excerpt="" <noscript>&lt;img src="https://www.yankodesign.com/images/design_news/2020/10/auto-draft/chipolo_ocean_2.jpg" alt="" width="1050" height="700" class="aligncenter size-full wp-image-282902" data-jpibfi-post-excerpt=""</noscript>'
# rex = re.compile('&lt;img class="alignnone size-full .*? src="(.*?)" alt')
# a = '<noscript>&lt;img src="https://www.yankodesign.com/images/design_news/2020/02/auto-draft/anicorn_redundant_watch-yankodesign02.jpg" data-jpibfi-post-excerpt="" data-jpibfi-post-url="https://www.yankodesign</noscript>'
# rex = re.compile('<noscript>&lt;img.*?src="(.*?)".*?</noscript>')
# print(rex.findall(a))

# a = 'https://ksr-ugc.imgix.net/assets/031/001/155/2d9c80cbbaa0a795121775a987349f13_original.gif?ixlib=rb-2.1.0&w=680&fit=max&v=1602682467&auto=format&gif-q=50&q=92&s=b8528d9b4e0c3e5aaa5a65267fc39f9f'
# b = 'https://ksr-ugc.imgix.net/assets/031/001/155/2d9c80cbbaa0a795121775a987349f13_original.gif?ixlib=rb-2.1.0&amp;amp;w=680&amp;amp;fit=max&amp;amp;v=1602682467&amp;amp;auto=format&amp;amp;gif-q=50&amp;amp;q=92&amp;amp;s=b8528d9b4e0c3e5aaa5a65267fc39f9f'
# # d = "https://ksr-ugc.imgix.net/assets/030/537/910/8044edb10b84a4e28fd5d19ce7050efa_original.gif?ixlib=rb-2.1.0&amp;#038;w=680&amp;#038;fit=max&amp;#038;v=1599678904&amp;#038;auto=format&amp;#038;gif-q=50&amp;#038;q=92&amp;#038;s=1a1634b209185741ef3fdcc545a92937"
# c = b.replace("amp;",'').replace("#038;","")
# print(c)


a = '''
If you’re a die-hard Tesla fan after yesterday’s absolutely mind-melting presentation, you’re not the only one!
Carry around a part of the automobile giant’s legacy around with the Tesla Powerbank. Made by Tesla, the Powerbank was designed and inspired after Tesla’s Supercharger monument. With a 3350mAh battery on the inside and circuitry to ensure fast charging to the maximum battery capacity, the Powerbank can charge both Android phones and iPhones, thanks to the dual connectors concealed in the Powerbank’s slick, heart-pumping design. Plus, if there’s any company that’s known for making the world’s best batteries, it’s Tesla, right?!
Designer: Tesla'''

b = re.search("Designer[s]*:[\s\S]*", a, )
d = b.group()

print(d)

a = '''

{
"@context": "http://schema.org/",
"@type": "Product",
"sku": "92590053",
"material": "Aluminium",
"model": "https://www.rimowa.com/cn/zh/%E9%93%B6%E8%89%B2/",
"height": "55 CM",
"width": "40 CM",
"depth": "23 CM",
"weight": "4,3 Kg",
"image": ["https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw5d7986df/images/large/92590053_1.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw6459c0f2/images/large/92590053_2.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dwbb52f5d2/images/large/92590053_3.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dwb5675008/images/large/92590053_4.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw02a6352a/images/large/92590053_5.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw2b10f592/images/large/92590053_6.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dwf6d84310/images/large/92590053_7.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw759e7ac4/images/large/92590053_8.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dwc9440e1a/images/large/92590053_9.png","https://www.rimowa.com/on/demandware.static/-/Sites-rimowa-master-catalog-final/default/dw88c484d9/images/large/92590053_10.png"],
"mpn": "92590053",
"brand": {
"@type": "Thing",
"name": "RIMOWA"
}
}'''

b = re.findall('"image": \["(.*)"\]', a)
c = b[0].split('","')
print(c)

text = ' Communication Design Category, 2010 - 2011.'
rex = re.compile(r'Category, (\d+) - (\d+)')
prize_time = rex.findall(text)
print(prize_time)



s = '商品评价(10万+)'
a = re.findall('商品评价\((.*)\)',s)
print(a)