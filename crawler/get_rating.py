import requests
import csv
import re
import time
import random

class GetRating(object):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}
        self.top250_ids = []
        self.user_passed = 0
        with open('../data/top250.csv', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.top250_ids.append(row[0])
        with open('../data/users.csv', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.user_set = row
        with open('../data/user_passed.csv', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.user_passed = int(row[0])

    def traverse(self):
        for i in range(self.user_passed, len(self.user_set)):
            succ = self.traverse_user(i)
            with open("../data/user_passed.csv", "w", encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([i+1])
            print('========== passed user:', i+1, ", success:", succ, '==========')
            time.sleep(random.uniform(2, 8))
        
    def traverse_user(self, user_index):
        uid = self.user_set[user_index]
        html = requests.get(f"https://movie.douban.com/people/{uid}/collect", headers=self.headers).text
        mv_num_match = re.search(r'看过的影视.\d+', html)
        if mv_num_match is None:
            return False
        mv_num = int(re.search(r'\d+', mv_num_match.group(0)).group(0))
        if mv_num >= 50:    # ignore users without sufficient ratings
            user_dict = {}
            for start_num in range(0, mv_num, 15):
                user_dict.update(self.traverse_page(uid, start_num))
            if len(user_dict) >= 10:
                row = [user_index]
                for i in range(len(self.top250_ids)):
                    if self.top250_ids[i] in user_dict:
                        row.append(user_dict[self.top250_ids[i]])
                    else:
                        row.append(0)
                with open("../data/user_rating.csv", "a", encoding='utf-8', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(row)
        return True

    def traverse_page(self, uid, start_num):
        page_dict = {}
        html = requests.get(f"https://movie.douban.com/people/{uid}/collect?start={start_num}", headers=self.headers).text
        html = re.sub('\n+', '', html)  # delete all \n for they cannot be matched by dot in re
        mv_matchs = re.findall(r'https://movie.douban.com/subject/\d+/.+?span class=.date', html)
        for mv_match in mv_matchs:
            mv_id = re.search(r'\d+', re.search(r'/subject/\d+/', mv_match).group(0)).group(0)
            if mv_id not in self.top250_ids:
                continue
            rating_match = re.search(r'rating\d-t', mv_match)
            if rating_match is None:
                continue
            rating = int(re.search(r'\d', rating_match.group(0)).group(0))
            page_dict[mv_id] = rating
        time.sleep(random.uniform(0.2, 2))
        return page_dict              

def main():
    get_rating = GetRating()
    get_rating.traverse()

if __name__ == "__main__":
    main()