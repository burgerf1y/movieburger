import time
import csv
import random
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By


class GetUser(object):
    def __init__(self):
        self.page_prf = 'https://douban.com/people/'
        self.page_suf = ['/contacts', '/rev_contacts']
        self.q = Queue()
        with open("../data/users.csv", encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.user_visited = set(row)
                for user in row:
                    self.q.put(user)
        self.driver = webdriver.Chrome()

    def traverse(self):
        login_url = 'https://accounts.douban.com/passport/login'
        self.driver.get(login_url)
        msg = input('input anything if you have successfully logged in\n')
        while not self.q.empty():
            cur_user = self.q.get()
            self.traverse_user(cur_user)
            with open("../data/users.csv", "w", encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(list(self.user_visited))
            print('========== visited users: ', len(self.user_visited), " ==========")

    def traverse_user(self, uid):
        self.driver.get(self.page_prf + uid + self.page_suf[0])
        self.traverse_page()
        self.driver.get(self.page_prf + uid + self.page_suf[1])
        self.traverse_page()

    def traverse_page(self):
        time.sleep(random.uniform(0.75, 1.5))
        user_links = self.driver.find_elements(By.XPATH, '//dt[@class="avatar-wrap"]//a')
        for user_link in user_links:
            text = user_link.get_attribute('href')
            new_user = text[30: -1]
            if new_user not in self.user_visited:
                self.user_visited.add(new_user)
                self.q.put(new_user)

def main():
    get_user = GetUser()
    get_user.traverse()

if __name__ == '__main__':
    main()
