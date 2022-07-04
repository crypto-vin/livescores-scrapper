import requests
from bs4 import BeautifulSoup
import time

payload={}
headers={}

URL = 'https://www.livescore.com/en/football/live/'
page = requests.get(URL)

def get_scores():
    soup = BeautifulSoup(page.content, 'lxml')
    try:
        teams = soup.find_all('div', class_="vk zk yk")
        print(teams)
    except Exception as e:
        print(e)

get_scores()