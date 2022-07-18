#Created by Vincent Munyalo

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
#from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

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
        #team = 'MCI'
        #self.team = team
        sports_url = 'https://www.flashscore.com/'
        self.sports_url = sports_url

    #get the flashscore site
    def get_site(self):
        self.driver.get(self.sports_url)
        try:
            element = WebDriverWait(self.driver, 20).until(
	            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[1]/div/div[1]/div[2]/div[4]/div[2]/div/div[1]/div/div[2]"))
	        )
            element.click()
            print('Element found')
        except:
            print('Element not found')
        
    #Identify the matches
    def get_live_matches(self):
        while True:
            home_team_list = []
            self.home_team_list = home_team_list
            away_team_list = []
            self.away_team_list = away_team_list
            home_score_list = []
            self.home_score_list = home_score_list
            away_score_list = []
            self.away_score_list = away_score_list

            try:
                home_teams = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//*[@class='event__participant event__participant--home']"))
                    )

                away_teams = self.driver.find_elements_by_xpath("//*[@class='event__participant event__participant--away']")
        
                
            except Exception as e:
                print(e)
            
            else:
                for home_team in home_teams:
                    home_team_list.append(home_team.text)
                for away_team in away_teams:
                    away_team_list.append(away_team.text)
                total = len(home_team_list)
                print(f'Total matches are: {total}')

                try: 
                    home_team_scores = self.driver.find_elements_by_xpath("//*[@class='event__score event__score--home']")
                    away_team_scores = self.driver.find_elements_by_xpath("//*[@class='event__score event__score--away']")
                except Exception as err:
                    print(err)
                
                else:
                    for score in home_team_scores:
                        home_score_list.append(score.text)
                    for score in away_team_scores:
                        away_score_list.append(score.text)


                away_team_total = len(away_team_list)
                home_score_total = len(home_score_list)
                away_score_total = len(away_score_list)


                print(f' Home Team List: {len(home_team_list)}')
                print(f' Away Team List: {away_team_total}')
                print(f' Home Score List: {len(home_score_list)}')
                print(f' Away Score List: {len(away_score_list)}')

                if away_team_total != away_score_total or home_score_total != total:
                    print('Results might be erroneous')
                
                elif away_team_total != total:
                    print('Results still erroneous')

                else:
                    with open('new_scores.csv', 'w', newline='') as f:
                        header = ['Home', 'Home Score', 'Away Score', 'Away']
                        write = csv.writer(f) 
                        write.writerow(header) 
                        for i in range(0, total):
                            print(f"{home_team_list[i]} {(home_score_list[i])} -  {(away_score_list[i])} {away_team_list[i]}")
                            data = [[str(home_team_list[i]), str(home_score_list[i]), str(away_score_list[i]), str(away_team_list[i])]]
                            write.writerows(data)

                    self.ascertain_goal()
                    #self.driver.quit()
                    time.sleep(10)
    
    #Determine whether a goal has been scored on not
    def ascertain_goal(self): 
        score_list = []
        df1 = pd.read_csv('new_scores.csv')
        df2 = pd.read_csv('scores.csv')
        
        df_current = pd.DataFrame(df1)
        df_previous = pd.DataFrame(df2)
        
        df = pd.merge(df_previous, df_current, how='inner', on =['Home', 'Away'])
        df

        total = df[df.columns[0]].count() 
        print(total)
        for i in range(0, total):
            if df['Home Score_x'][i] == (df['Home Score_y'][i]) and df['Away Score_x'][i] == (df['Away Score_y'][i]):
                #print('No goal')
                team = df['Home'][i]
                
            elif df['Home Score_x'][i] < (df['Home Score_y'][i]):
                team = df['Home'][i]
                print(team + ' has scored')
                score_list.append(team)
                
            elif df['Away Score_x'][i] < (df['Away Score_y'][i]):
                team = df['Away'][i]
                print(team + ' has scored')
                score_list.append(team)

            else:
                print('goal disallowed')

        df_current.to_csv('scores.csv', index=False)

    
    def send_data(self):
        response = requests.get(url=self.sports_url)
        response_data = response.json().get('data')

        for data in response_data:
            print(data)
        return_data = []
        


    #run the program
    def run(self):
        self.get_site()
        self.get_live_matches()
        #self.get_data()

if __name__ == '__main__':
    bsl = Super_League()
    bsl.run()
