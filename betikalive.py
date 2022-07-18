#Created by Vincent Munyalo

from turtle import home
import selenium
from selenium import webdriver
from getpass import getpass
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
import json
import time
import csv
import pandas as pd
from difflib import SequenceMatcher
from client import Client

class Super_League:
    #initialize Super League class
    def __init__(self):
        PATH = "C:\Program Files (x86)\chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'] )
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', {'credentials_enable_service': False, 'profile': {'password_manager_enabled': False }})
        self.driver = webdriver.Chrome(executable_path = PATH, options=chrome_options)
        sports_url = 'https://www.flashscore.com/'
        self.sports_url = sports_url
        self.home_team = ''
        self.away_team = ''
        self.scorer = ''
        self.hometeam = ''
        self.awayteam = ''
        self.home_score = ''
        self.away_score = ''
        with open('new_scores.csv', 'w', newline='') as f:
            header = ['Home', 'Home Score', 'Away Score', 'Away']
            write = csv.writer(f) 
            write.writerow(header)

    #get the flashscore site
    def get_site(self):
        self.driver.get(self.sports_url)
        try:
            element = WebDriverWait(self.driver, 20).until(
	            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[1]/div/div[1]/div[2]/div[4]/div[2]/div/div[1]/div/div[2]"))
	        )
            element.click()
            print('Searching for a goal...')
        except:
            print('Live section not found')
        
        try:
            accept = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
                )
            accept.click()
        except Exception as e:
            print(e)
        
    #Identify the matches with a goal
    def get_live_matches(self):
        home_team_list = []
        self.home_team_list = home_team_list
        away_team_list = []
        self.away_team_list = away_team_list
        home_score_list = []
        self.home_score_list = home_score_list
        away_score_list = []
        self.away_score_list = away_score_list
        count = 0
        home_index = 0
        away_index = 0
        try:
            home_teams = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*[@class='event__participant event__participant--home']"))
                )

        except Exception as e:
            print(e)

        else:
        #infinite goal-searching loop
            while True:
                try:
                    home_teams_scored = self.driver.find_elements_by_xpath("//*[@class='event__participant event__participant--home highlighted']")
                    home_teams_scores = self.driver.find_elements_by_xpath("//*[@class='event__score event__score--home highlighted']")
        
                except:
                    print('No home team has scored')
                
                else:
                    for home_team in home_teams_scored:
                        home_scorer = self.get_team(home_team.text)
                        for home_score in home_teams_scores:
                            home_score = home_score.text

                        if home_scorer not in home_team_list:
                            home_team_list.append(home_scorer)
                            home_score_list.append(home_score)
                            print(home_score_list)
                            print(home_index)
                            home_goal = home_score_list[home_index]
                            print(f"{home_scorer} has scored, score = {home_goal}")
                            next_goal = int(home_goal)
                            try:
                                Client().send_msg(f'{home_scorer},{next_goal}')
                            except:
                                print('Client unreachable!')
                            print(home_team_list, home_score_list)
                            count = 1
                            self.home_score = home_score_list[home_index]
                            home_index +=1

                        self.scorer = home_scorer
                        self.home_team = home_team
                        
                    self.check_score()  
                       
                try: 
                    away_teams_scored = self.driver.find_elements_by_xpath("//*[@class='event__participant event__participant--away highlighted']")
                    away_teams_scores = self.driver.find_elements_by_xpath("//*[@class='event__score event__score--away highlighted']")
                except Exception as err:
                    print('No away team has scored')
                
                else:
                    for away_team in away_teams_scored:
                        away_scorer = self.get_team(away_team.text)
                        for away_score in away_teams_scores:
                            away_score = away_score.text

                        if away_scorer not in away_team_list:
                            away_team_list.append(away_scorer)
                            away_score_list.append(away_score)
                            print(away_index)
                            print(away_score_list)
                            away_goal = away_score_list[away_index]
                            print(f"{away_scorer} has scored, score = {away_goal}")
                            next_goal = int(away_goal)
                            try:
                                Client().send_msg(f'{away_scorer},{next_goal}')
                            except:
                                print('Client unreachable!')
                            print(away_team_list, away_score_list)
                            count = 1
                            self.away_score = away_score_list[away_index]
                            away_index += 1
                        self.scorer = away_scorer
                        self.away_team = away_team
                        
                    self.check_score()
    
                #after 200 loops clear first element in the list and print the new list
                if count % 200 == 0:
                    print(count)
                    try:
                        home_team_list.pop(0)
                        away_team_list.pop(0)
                        home_score_list.pop(0)
                        away_score_list.pop(0)
                        home_index -=1
                        away_index -=1
                        print(f'Home team list: {home_team_list}')
                        print(f'Away team list: {away_team_list}')
                    except:
                        print('No items in the list') 
                
                if len(home_team_list) > 10:
                    home_team_list.pop(0)
                
                if len(away_team_list) > 10:
                    away_team_list.pop(0)

                if len(home_score_list) > 10:
                    home_score_list.pop(0)
                    home_index -=1

                if len(away_score_list) > 10:
                    away_score_list.pop(0)
                    away_index -=1

                count +=1
                time.sleep(0.25)

    #Split team name from country
    def get_team(self, name):
        team = name.split()
        try:
            team.pop()
        except:
            team_name = team
        else:
            team_name = ' '.join(team)
        return team_name

    #ascertain if selected team matches with teams on site
    def similar(self, a, b):
        similarity =  SequenceMatcher(None, a, b).ratio()
        if similarity > 0.6:
            return True
        else:
            return False

    #get json data on live games at the moment
    def get_live(self):
        self.live_checker = False
        URL = 'https://live.betika.com/v1/uo/matches?page=1&limit=1000&sub_type_id=1,186,340&sport=14&sort=1'
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


        betikalive = json.loads(response.text)
        self.betikalive = betikalive

    def strip_score(self, score, pos):
        if pos == 0:
            score = score[:1]
        if pos == 2:
            score = score[2:]
        return score

    #check match score from betika
    def check_score(self):
        self.get_live()
        jsondata = self.betikalive

        for game in jsondata['data']:
            league = game['competition']
            hometeam = game['home_odd_key']
            awayteam = game['away_odd_key']
            #game_id = game['game_id']
            match_id = game['match_id']
            score = game['current_score']

            #print(hometeam, awayteam)
            if self.home_team:
                if(self.similar(self.scorer, hometeam)) == True:
                    print(f'{self.scorer} is in live games, score: {score}')
                    betika_score = self.strip_score(score, 0)
                    self.hometeam = hometeam
                    print(f'Betika Score: {betika_score}, Flashscore Score: {self.home_score}')
                    if betika_score < self.home_score:
                        Bet().run(hometeam, 0)
                        break
                    else:
                        print('Match has been updated')
                        time.sleep(20)
                #else:
                    #print('Game not available in livematches')
                    
                    
            if self.away_team:
                if(self.similar(self.scorer, awayteam)) == True:
                    print(f'{self.scorer} is in live games, score: {score}')
                    self.awayteam = awayteam
                    betika_score = self.strip_score(score, 2)
                    print(f'Betika Score: {betika_score}, Flashscore Score: {self.away_score}')
                    if betika_score < self.away_score:
                        Bet().run(awayteam, 2)
                        break
                    else:
                        print('Match has been updated')
                        time.sleep(20)

    #run the program
    def run(self):
        self.get_site()
        self.get_live_matches()

class Bet:
    def __init__(self):
        self.stake = '1'
        self.headers = {
            'authority': 'live.betika.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'dnt': '1',
            'if-modified-since': 'Wed, 06 Jul 2022 07:58:33 GMT',
            'origin': 'https://www.betika.com',
            'referer': 'https://www.betika.com/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

        self.json_data = {
            'mobile': '0712897106',
            'password': 'Vin2am@254',
            'remember': True,
            'src': 'MOBILE_WEB',
        }

        self.streamable_true = {
            'parent_match_id': '',
            'streamable': 'true',
        }

        self.streamable_null = {
            'id': '',
        }

        self.bet_data = {
            'profile_id': '',
            'stake': '',
            'total_odd': '',
            'src': 'MOBILE_WEB',
            'betslip': [],
            'token': '',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
            'app_version': '6.0.0',
            'affiliate': None,
            'promo_id': None,
            'fbpid': False,
            'is_freebet': False,
        }

    def livebet(self, live, s, index):
        self.streamable_true['parent_match_id'] = live['parent_match_id']
        self.streamable_null['id'] = live['match_id']
        streamable = live['streamable']
        
        if streamable == None:
            response = s.get('https://live.betika.com/v1/uo/match', params=self.streamable_null, headers=self.headers)
            response_text = json.loads(response.text)
            #print(response_text)
        else:
            response = s.get('https://live.betika.com/v1/uo/match', params=self.streamable_true, headers=self.headers)
            response_text = json.loads(response.text)
            #print(response_text)
        
        data = response_text['data']
        
        for key in data:
            sub_type_id = key['sub_type_id']
            #print(sub_type_id)

            slip = []
            if sub_type_id == 8:
                name = key['name']
                market_active = key['market_active']
                #index = 0 #TODO the index to be varying between 0--home and 2--away depending on which side there is a goal
                odds = key['odds'][index]
                if market_active == 1: #TODO Add a condition which checks if the goal has not been updated eg WHO WILL SCORE 2ND GOAL text split to get 2 from 2ND
                    game = {}
                    game['sub_type_id']= 8
                    game['bet_pick']= odds['odd_key']
                    game['odd_value']= odds['odd_value']
                    game['outcome_id']= odds['outcome_id']
                    game['special_bet_value']= odds['special_bet_value']
                    game['parent_match_id']= live['parent_match_id']
                    game['bet_type']= 8
                    
                    slip.append(game)

                    print(slip)

                    self.bet_data['betslip'] = slip
                    self.bet_data['total_odd'] = odds['odd_value']
                    print(self.bet_data)

                    response = requests.post('https://api.betika.com/v2/bet', headers=self.headers, json=self.bet_data)
                    response_text = response.text
                    response_text = json.loads(response_text)
                    print(response_text)
                else:
                    print('The selection is inactive')

    def check_live_bet(self, s, team, index):
        response = s.get('https://live.betika.com/v1/uo/matches?page=1&limit=1000&sub_type_id=1,186,340&sport=14&sort=1', headers=self.headers)
        response_text = json.loads(response.text)
        #print(response_text)

        data = response_text['data']
        lives = []
        for key in data:
            game = {}
            if key['home_team'] == team or key['away_team'] == team:
                print(f'Team has been found in Betika!')
                game['active']= key['active']
                game['start_time']= key['start_time']
                game['NOW']= key['NOW']
                game['parent_match_id']= key['parent_match_id']
                game['match_id']= key['match_id']
                game['current_score']= key['current_score']
                game['home_team']= key['home_team']
                game['away_team']= key['away_team']
                game['streamable']= key['streamable']
                game['match_id']= key['match_id']
                lives.append(game)
                #print(lives)

        #TODO The games to be filtered by the results of livescores.py    
        for live in lives: #TODO remove index limitation
            self.livebet(live,s, index)



    def run(self, team, index):
        #login and maintain the session
        with requests.Session() as s:
            response = s.post('https://api.betika.com/v1/login', headers=self.headers, json=self.json_data)
            response_text = response.text
            response_text = json.loads(response_text)
            #print(response_text)

            try:
                id = response_text['data']['user']['id']
            except Exception as err:
                print(err)
            else:
                token = response_text['token']
                self.bet_data['stake'] = self.stake
                self.bet_data['profile_id'] = id
                self.bet_data['token'] = token
                with open('data.json', 'w') as f:
                    json.dump(self.bet_data, f)

                self.check_live_bet(s, team, index)  

if __name__ == '__main__':
    bsl = Super_League()
    bsl.run()
