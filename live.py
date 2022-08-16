#Created by Vincent Munyalo

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
from difflib import SequenceMatcher
import socket

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
        prev_message = ''
        message_list = []
        
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
                    if count % 300 == 0:
                        print('No home team has scored')
                
                else:
                    home_index = 0
                    for home_score in home_teams_scores:
                        home_score = home_score.text
                        home_score_list.append(home_score)

                    for home_team in home_teams_scored:
                        home_scorer = self.get_team(home_team.text)
                        home_team_list.append(home_scorer)
                        
                        try:
                            home_goal = home_score_list[home_index]
                            next_goal = int(home_goal)
                            message = f'{home_scorer},{next_goal}'
                            if message not in message_list:
                                print(f"{home_scorer} has scored, score : {home_goal}")
                                Client().send_msg(message)
                                message_list.append(message)
                        except:
                            print('Client unreachable!')
                        else:
                            prev_message = message

                        count = 1
                        self.home_score = home_goal
                        home_index +=1

                        self.scorer = home_scorer
                        self.home_team = home_team 

                    home_team_list.clear()
                    home_score_list.clear()
                       
                try: 
                    away_teams_scored = self.driver.find_elements_by_xpath("//*[@class='event__participant event__participant--away highlighted']")
                    away_teams_scores = self.driver.find_elements_by_xpath("//*[@class='event__score event__score--away highlighted']")

                except Exception as err:
                    if count % 300 == 0:
                        print('No away team has scored')
                
                else:
                    away_index = 0
                    for away_score in away_teams_scores:
                        away_score = away_score.text
                        away_score_list.append(away_score)

                    for away_team in away_teams_scored:
                        away_scorer = self.get_team(away_team.text)
                        away_team_list.append(away_scorer)
                        
                        try:
                            away_goal = away_score_list[away_index]
                            next_goal = int(away_goal)
                            message = f'{away_scorer},{next_goal}'
                            if message not in message_list:
                                print(f"{away_scorer} has scored, score : {away_goal}")
                                Client().send_msg(message)
                                message_list.append(message)
                        except:
                            print('Client unreachable!')
                        else:
                            prev_message = message
                        count = 1
                        self.away_score = away_goal
                        away_index += 1

                        self.scorer = away_scorer
                        self.away_team = away_team
                    
                    away_team_list.clear()
                    away_score_list.clear()

                if len(message_list) > 10:
                    message_list.pop(0)
        
                count +=1
                time.sleep(0.15)

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

    #run the program
    def run(self):
        self.get_site()
        self.get_live_matches()

class Client:
    #initialize the client class
    def __init__(self):
        self.HEADER = 64
        self.PORT = 5080
        self.SERVER = '127.0.0.1'
        self.FORMAT = 'utf-8'
        self.ADDR = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    #send message to the server
    def send_msg(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
    
    #Run the client side
    def run(self, scorer, score):
        msg = input('Enter team and score: ')
        self.send_msg(msg)  

if __name__ == '__main__':
    bsl = Super_League()
    bsl.run()
