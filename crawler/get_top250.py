import requests
import csv
from bs4 import BeautifulSoup as BS

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
}   # pretend to be firefox
for start_num in range(0, 250, 25):
    response = requests.get(f"https://movie.douban.com/top250?start={start_num}", headers = headers)
    soup = BS(response.text, "html.parser")
    all_titles = soup.findAll("span", attrs={"class": "title"})
    for title in all_titles:
        title_str = title.string
        if "/" not in title_str:    # only focus on Chinese title of movie
            href_str = title.parent.attrs['href']
            filmid_str = ''
            for i in href_str:
                if str.isdigit(i):
                    filmid_str += i
            row = [filmid_str, title_str]
            with open("../data/top250.csv", "a", encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)