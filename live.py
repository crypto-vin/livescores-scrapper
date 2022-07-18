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
                        
                    #self.check_score()  
                       
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
                            try:
                                next_goal = int(away_goal)
                                Client().send_msg(f'{away_scorer},{next_goal}')
                            except:
                                print('Client unreachable!')
                            print(away_team_list)
                            count = 1
                            self.away_score = away_score_list[away_index]
                            away_index += 1
                        self.scorer = away_scorer
                        self.away_team = away_team
                        
                    #self.check_score()
    
                #after 100 loops clear first element in the list and print the new list
                if count % 100 == 0:
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
                
                if len(home_team_list) > 5:
                    home_team_list.pop(0)
                
                if len(away_team_list) > 5:
                    away_team_list.pop(0)

                if len(home_score_list) > 5:
                    home_score_list.pop(0)
                    home_index -=1

                if len(away_score_list) > 5:
                    away_score_list.pop(0)
                    away_index -=1

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

    #ascertain if selected team matches with teams on site
    def similar(self, a, b):
        similarity =  SequenceMatcher(None, a, b).ratio()
        #print(similarity)
        if similarity > 0.6:
            return True
        else:
            return False

    #run the program
    def run(self):
        self.get_site()
        self.get_live_matches()

if __name__ == '__main__':
    bsl = Super_League()
    bsl.run()
