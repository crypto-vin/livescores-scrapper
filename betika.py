import requests
import json
import time

payload={}
headers={}

URL = 'https://live.betika.com/v1/uo/matches?page=1&limit=1000&sub_type_id=1,186,340&sport=14&sort=1'

def get_live():
    headers = {
    'authority': 'api.betika.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'if-modified-since': 'Tue, 05 Jul 2022 11:58:40 GMT',
    'origin': 'https://www.betika.com',
    'referer': 'https://www.betika.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36',
    }

    response = requests.get(URL, headers=headers)
    data = response.text
    with open('betikalive.txt', 'w') as f:
        f.write(data)


    a = json.loads(response.text)
    print(a)

get_live()
