import re
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import *
import pymongo

##有AJAX请求，可以选用这个模板

client = pymongo.MongoClient()
db = client[MONGO_DB]

#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
browser = webdriver.Chrome()#chrome_options=chrome_options)
wait = WebDriverWait(browser, 10)


def search_page():#第一页的状态设置
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com/')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        input.send_keys('运动鞋')
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_product()
        return total.text
    except TimeoutException:
        return search_page()

def next_page(page_number):#后续要进行的设置
    print('正在搜索')
    try:
        input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )
        get_product()
    except TimeoutException:
        next_page(page_number)

def get_product():#得到目标信息
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        #save_to_mongo(product)

#def save_to_mongo(result):#存进可视化数据库中
    #try:
        #if db[MONGO_TABLE].insert(result):
            #print('成功写入', result)
           # return True
        #return False
    #except Exception:
        #pass


def main():
    total = search_page()#第一步拿到信息，才能有TOTAL这数据出来
    total = int(re.compile('(\d+)').search(total).group(1))#拿到我们要爬的总页数
    print(total)
    #for i in range(2, total+1):
       # next_page(i)
    browser.close()


if __name__ == '__main__':
    main()
