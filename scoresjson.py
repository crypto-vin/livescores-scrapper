import json

with open('response.json') as f:
    jsondata = json.load(f)

league = jsondata['events'][0]['tournament']['name']
hometeam = jsondata['events'][0]['homeTeam']['name']
awayteam = jsondata['events'][0]['awayTeam']['name']
homescore = jsondata['events'][0]['homeScore']['current']
awayscore = jsondata['events'][0]['awayScore']['current']


for game in jsondata['events']:
    league = game['tournament']['name']
    hometeam = game['homeTeam']['name']
    awayteam = game['awayTeam']['name']
    homescore = game['homeScore']['current']
    awayscore = game['awayScore']['current']
    print(league, ' | ', hometeam, homescore, ' - ', awayscore, awayteam)