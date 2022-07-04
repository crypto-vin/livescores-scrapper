import requests
import json

url = "https://api.sofascore.com/api/v1/sport/football/events/live"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

jsondata = json.loads(response.text)

for game in jsondata['events']:
    league = game['tournament']['name']
    hometeam = game['homeTeam']['name']
    awayteam = game['awayTeam']['name']
    homescore = game['homeScore']['current']
    awayscore = game['awayScore']['current']
    print(league, ' | ', hometeam, homescore, ' - ', awayscore, awayteam)