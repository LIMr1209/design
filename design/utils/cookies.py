
# cookies 字符串转字典
def cookie_to_dic(cookie):
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}