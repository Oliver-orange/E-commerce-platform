from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime

# 初始化 WebDriver
driver = webdriver.Edge()


def setup():
    # 打开网站
    driver.get('http://127.0.0.1:5000/')


def handle_alert():
    """处理可能出现的 JavaScript 弹窗"""
    try:
        alert = driver.switch_to.alert
        alert.accept()  # 接受弹窗
    except Exception as e:
        print("No alert present", e)


def test_register_and_login():
    """测试用户注册功能和登录功能"""
    driver.get('http://127.0.0.1:5000/login')

    # 1. 注册新用户
    driver.find_element(By.LINK_TEXT, 'Register here').click()  # 点击注册链接
    driver.find_element(By.ID, 'username').send_keys('newuser')  # 输入新用户名
    driver.find_element(By.ID, 'email').send_keys('newemail@email.com')  # 输入新邮箱
    driver.find_element(By.ID, 'password').send_keys('newpassword')  # 输入新密码
    driver.find_element(By.XPATH, '//button[text()="Register"]').click()  # 点击注册按钮
    time.sleep(1)  # 等待页面加载

    # 2. 登录新注册的用户
    driver.find_element(By.ID, 'username').send_keys('newuser')  # 输入新用户名
    driver.find_element(By.ID, 'password').send_keys('newpassword')  # 输入新密码
    driver.find_element(By.XPATH, '//button[text()="Login"]').click()  # 点击登录按钮


def test_add_to_cart():
    """测试将产品添加到购物车"""
    products = driver.find_elements(By.CLASS_NAME, 'product')
    for product in products[:1]:  # 只添加第一个产品
        product.get_attribute('data-id')
        product.find_element(By.XPATH, './/button[text()="Add to Cart"]').click()
        time.sleep(1)  # 等待添加完成
        handle_alert()


def test_cart():
    """测试购物车内容"""
    driver.get('http://127.0.0.1:5000/cart')
    cart_items = driver.find_elements(By.CSS_SELECTOR, '#cart-items ul li')
    assert len(cart_items) > 0, "购物车为空"
    handle_alert()


def test_checkout():
    """测试结账功能"""
    driver.find_element(By.XPATH, '//button[text()="Proceed to Checkout"]').click()
    time.sleep(2)
    handle_alert()
    assert "Checkout completed!" in driver.page_source, "Checkout failed"


def test_ui_elements():
    """UI 测试"""
    driver.get('http://127.0.0.1:5000/')
    assert "Product Listings" in driver.page_source, "页面标题不正确"
    driver.get('http://127.0.0.1:5000/login')
    assert "Login" in driver.page_source, "未找到登录标题"
    driver.get('http://127.0.0.1:5000/register')
    assert "Register" in driver.page_source, "未找到注册标题"


def test_invalid_login():
    """测试无效登录"""
    driver.get('http://127.0.0.1:5000/login')
    driver.find_element(By.ID, 'username').send_keys('invaliduser')
    driver.find_element(By.ID, 'password').send_keys('invalidpassword')
    driver.find_element(By.XPATH, '//button[text()="Login"]').click()
    time.sleep(2)
    assert "Invalid username or password" in driver.page_source, "未正确处理无效登录"


def teardown():
    """关闭 WebDriver"""
    driver.quit()


if __name__ == "__main__":
    setup()
    start_time = datetime.now()  # 记录测试开始时间
    print("Starting tests...")

    try:
        test_register_and_login()
        test_add_to_cart()
        test_cart()
        test_checkout()
        test_ui_elements()
        test_invalid_login()
    finally:
        end_time = datetime.now()  # 记录测试结束时间
        duration = end_time - start_time  # 计算用时
        print(f"Tests completed in: {duration}")
        teardown()
