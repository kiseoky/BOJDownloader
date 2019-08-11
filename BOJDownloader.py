from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import mimetypes
from bs4 import BeautifulSoup
import requests
#from github import Github
import threading
import os

def BOJDownlaod(user_id, user_pw):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome('chromedriver', options=options)

    driver.get('https://www.acmicpc.net/login')


    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        while True:
            if not driver.find_element_by_name("login_user_id").get_attribute('value'):
                driver.find_element_by_name("login_user_id").clear()
                driver.find_element_by_name("login_user_id").send_keys(user_id)
            if not driver.find_element_by_name("login_password").get_attribute('value'):
                driver.find_element_by_name("login_password").clear()
                driver.find_element_by_name("login_password").send_keys(user_pw)
            if driver.find_element_by_name("login_user_id").get_attribute('value') and \
               driver.find_element_by_name("login_password").get_attribute('value'):
                driver.find_element_by_id("submit_button").click()
    except:
        pass
    while not driver.current_url == 'https://www.acmicpc.net/':
        pass
        #print(driver.current_url)

    cookies = driver.get_cookies()

    driver.quit()

    s = requests.Session()

    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
        
    html = s.get('https://www.acmicpc.net/user/'+user_id).text
    class Problem:
        def __init__(self, num):
            self.num = num
            self.name = ""
            self.code = ""
            self.extension = ""
        def __str__(self):
            return f"{self.num}.{self.extension}"
    def getCode(p):
        html = s.get(f'https://www.acmicpc.net/status?from_mine=1&problem_id={p}&user_id={user_id}').text
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.select('#status-table > tbody > tr'):        
            if tr.find('td', {'class' : 'memory'}).text:
                td = tr.find_all('td')[2].find('a')['title']
                p.name = td
                num = tr.find('td').text
                source = s.get(f'https://www.acmicpc.net/source/download/{num}')
                p.extension = source.headers['Content-Disposition'][source.headers['Content-Disposition'].rfind(".")+1:-1]
                p.code = source.text.replace('\r','')
                
                if not os.path.exists('BOJ codes'):
                    os.makedirs('BOJ codes')                
                with open('BOJ codes/'+p.__str__(), 'w') as f:
                    f.write(p.code)
                print(f'{p}\n')
                break
        
    soup = BeautifulSoup(html, 'html.parser')
    solved = [Problem(a.text) for a in soup.find("div", {"class": "panel-body"}).find_all("span", {"class" : "problem_number"})]

    start_t = time.time()

    for p in solved:
       t = threading.Thread(target=getCode, args=[p])
       t.start()



    for thread in threading.enumerate():
        if thread.daemon:
            continue
        try:
            thread.join()
        except RuntimeError as err:
            if 'cannot join current thread' in err.args[0]:
                # catchs main thread
                continue
            else:
                raise

    #141.17 -> 9.73 secs
u_id = input("input ID: ")
u_pw = input("input PW: ")

BOJDownlaod(u_id, u_pw)
print('BOJ codes 폴더에 저장되었습니다.')
