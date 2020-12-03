from selenium.webdriver import ActionChains
from selenium import webdriver
import time
import selenium.webdriver.support.ui as ui
import random


def get_track(distance):  # distance为传入的总距离
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 0

    while current < distance:
        if current < mid:
            # 加速度为2
            a = 2
        else:
            # 加速度为-2
            a = -3
        v0 = v
        # 当前速度
        v = v0 + a * t
        # 移动距离
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track


def move_to_gap(slider, tracks):  # slider是要移动的滑块,tracks是要传入的移动轨迹
    ActionChains(driver).click_and_hold(slider).perform()
    for x in tracks:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(driver).release().perform()


driver = webdriver.Chrome(executable_path="D:/selenium/chrome/chromedriver.exe")
wait = ui.WebDriverWait(driver, 20)
driver.get("xxx")
time.sleep(1)
for i in range(5):
    driver.find_element_by_id('username').send_keys('admin123321')  # 输入用户名
    time.sleep(1)
    driver.find_element_by_id('password').send_keys('admin123321!@#')  # 输入密码
    time.sleep(1)
    driver.find_element_by_id('tel').send_keys('xxxx')  # 输入手机号
    #
    ActionChains(driver).click(wait.until(lambda x: x.find_element_by_css_selector(
        "#main-wrap > div > div.register-content > div.message > span"))).perform()
    iframe = wait.until((lambda driver: driver.find_element_by_id('tcaptcha_popup')))
    driver.switch_to.frame(iframe)
    #
    button = wait.until((lambda driver: driver.find_element_by_id('tcaptcha_drag_thumb')))
    distance = random.randint(225, 230)
    # 这有个bug，有时候不会移动
    move_to_gap(button, get_track(distance))
    time.sleep(random.randint(5, 8))
    driver.refresh()
    time.sleep(1.5)
