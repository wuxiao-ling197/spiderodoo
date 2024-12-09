import csv
import time
import requests  # send requests
# import useragent
from lxml import etree  # lxml is third web-coeded library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

murl = []
purl = []
aurl = ''
purl.append('https://apps.odoo.com/apps/modules/browse?series=17.0&price=Free')


# 从网页url获取资源链接
def get_module_url():
    # 获取网页源代码  https://apps.odoo.com/apps/modules/browse?search=hr
    global url, aurl
    Wurl = 'https://apps.odoo.com/apps/modules/browse?series=17.0&price=Free'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    response = requests.get(Wurl, headers=headers, timeout=30)
    html = response.text

    # 2、解析网页
    parse = etree.HTML(html)
    # XPath:   //*[@id="loempia_app_infos"]/div[3]/table/tbody/tr[1]/td[2]
    soup = BeautifulSoup(html, 'html.parser')
    print("start purl...")
    # 获取全部分页
    for page in soup.select('div[class="col-12 text-center mt32 mb24"] ul li a'):
        url = page.get('href')
        aurl = aurl + url
        # 判断是否有重复路径
        if aurl.find(url) == -1:
            purl.append("https://apps.odoo.com" + url)
    for i in range(2, 73):
        if aurl.find('page/' + str(i) + '/') == -1:
            url = 'https://apps.odoo.com/apps/modules/browse/page/' + str(i) + '?series=17.0&price=Free'
            purl.append(url)
    print("finish purl")

    # 获取all模块url
    print("start murl...")
    for p in purl:
        response = requests.get(p, headers=headers, timeout=30)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        for items in soup.find_all('div', class_='loempia_app_entry loempia_app_card col-md-6 col-lg-3'):
            item = items.select('a')[0]
            mhref = item.get('href')
            murl.append("https://apps.odoo.com" + mhref)
            with open('url.txt','a',encoding='utf_8_sig') as f:
                f.writelines("https://apps.odoo.com" + mhref +"\n")
        # print(len(murl))
    print("finish murl.")


def get_rsurl_from_html():
    with open(r'C:\Users\tibird\Desktop\1600.html', 'r', encoding='utf-8') as f:
        Soup = BeautifulSoup(f.read(), 'html.parser')
        urls = Soup.find_all('a')
        count = 0

        for url in urls:
            murl.append(url.get('href'))
            count =count + 1
            print(url.get('href'))
        print("finish ", count)


# 从资源链接url获取资源信息
def get_module_info():
    for m in murl:
        print(m)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        response = requests.get(m, headers=headers, timeout=30)
        html = response.text
        parse = etree.HTML(html)
        all_tr = parse.xpath('//*[@id="loempia_app_infos"]')
        for tr in all_tr:
            tr = {
                'Module-Name': ''.join(tr.xpath('./div[1]/div[1]/h1/b/text()')).strip(),
                'Technical-Name': ''.join(tr.xpath('./div[3]/table/tbody/tr[1]/td[2]/code/text()')).strip(),
                # 'Download':''.join(tr.xpath('./div[1]/div[3]/div/div[1]/a/div[2]/div[3]/span[2]/span/text()')).strip(),
                # 'Availability':''.join(tr.xpath('./div[3]/table/thead/tr[1]/td[2]/span/text()')).strip(),
                'OdooApps-Dependencies': ''.join(tr.xpath('./div[3]/table/thead/tr[2]/td[2]/span/text()')).strip(),
            }
            print(tr)
            with open('modules.csv', 'a', encoding='utf_8_sig', newline='') as fp:
                # a为追加模式 utf_8_sig模式导出不乱码
                fieldnames = ['Module-Name', 'Technical-Name', 'OdooApps-Dependencies']
                writer = csv.DictWriter(fp, fieldnames)
                writer.writerow(tr)
                print("保存成功")


# 测试单个资源链接点击下载功能
def _single():
    # Wurl = 'https://apps.odoo.com/apps/modules/17.0/cloud_base/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    response = requests.get('https://apps.odoo.com/apps/modules/17.0/cloud_base/', headers=headers, timeout=30)
    html = response.text
    parse = etree.HTML(html)
    all_tr = parse.xpath('//*[@id="loempia_app_infos"]')
    for tr in all_tr:
        tr = {
            'Module-Name': ''.join(tr.xpath('./div[1]/div[1]/h1/b/text()')).strip(),
            'Technical-Name': ''.join(tr.xpath('./div[3]/table/tbody/tr[1]/td[2]/code/text()')).strip(),
            # 'Download':''.join(tr.xpath('./div[1]/div[3]/div/div[1]/a/div[2]/div[3]/span[2]/span/text()')).strip(),
            # 'Availability':''.join(tr.xpath('./div[3]/table/thead/tr[1]/td[2]/span/text()')).strip(),
            'OdooApps-Dependencies': ''.join(tr.xpath('./div[3]/table/thead/tr[2]/td[2]/span/text()')).strip(),

        }
        # module['Module-Name']= ''.join(tr.xpath('./div[3]/table/tbody/tr[1]/td[2]/code/text()')).strip()
        # module['Technical-Name']= ''.join(tr.xpath('./div[3]/table/tbody/tr[1]/td[2]/code/text()')).strip()
        print(tr)
    dlstr = parse.xpath('//*[@id="buy_button"]')
    print(dlstr.text())

# 点击下载
def _download():
    opt = webdriver.ChromeOptions()
    # opt.page_load_strategy = 'normal'
    # 安装chromedriver 消除指纹
    opt.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    location = 'https://apps.odoo.com/apps'
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    print(ua)
    opt.add_argument('--user-agent=%s' % ua)
    opt.add_argument('--location=%s' % location)
    driver = webdriver.Chrome(options=opt)
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #     Object.defineProperty(navigator, 'webdriver', {
    #       get: () => undefined
    #     })
    #   """
    # })
    # driver.implicitly_wait(10)
    count = 0

    print("start...")
    for m in murl:
        driver.get(m)

        form = driver.find_element(by=By.XPATH, value='/html/body/div[1]/main/div[1]/div[1]/div[1]/div[2]/form[1]')
        btnprice = driver.find_element(by=By.XPATH, value='/html/body/div[1]/main/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]')
        # print("price=", btnprice.text)
        if form.text.find("Download") != -1:
            ##手动重定位 但可能仍然被识别
            driver.execute_script("window.location.href = 'https://apps.odoo.com/apps'")
            time.sleep(3)
            # 然后再进入需要的模块下载页
            driver.execute_script("window.location.href = '%s'" % m)
            time.sleep(3)
            # 最后查找元素模拟点击
            button = driver.find_element(by=By.XPATH, value='/html/body/div[1]/main/div[1]/div[1]/div[1]/div[2]/form[1]/a[1]')
            # 法一 直接模拟点击按钮 但点击按钮的模拟操作不稳定，有时候点击没反应
            # btndl.click()
            # 法二 JS注入单击
            driver.execute_script("arguments[0].click();", button)
            wait = WebDriverWait(driver, 10)#等待页面加载
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/main/div[1]/div[1]/div[1]/div[2]/form[1]/a[1]')))
            print("current_url=", driver.current_url)
            print("下载成功")
        else:
            print(btnprice.text)
            with open('undl.txt', 'a', encoding='utf_8_sig') as f:
                f.writelines(driver.title + m + "\n")
        time.sleep(5)
        count += 1
        print(count)
    print("！！！finish！！！")

if __name__ == '__main__':
    # _single()
    # get_module_url()
    get_rsurl_from_html()
    _download()
    # get_module_info()