
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from difflib import SequenceMatcher
import socket
import sys
import threading

class Mozzart:
    #initialize Mozzart class
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
        self.url = 'https://www.mozzartbet.co.ke/en#/live/sport/1'
        self.stake = 10
        self.HEADER = 64
        port = 5080
        self.PORT = port
        self.SERVER = '127.0.0.1'
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        
    #get the mozzart live site
    def get_site(self):
        self.driver.get(self.url)
        try:
            element = WebDriverWait(self.driver, 20).until(
	            EC.presence_of_element_located((By.XPATH, "//*[@class='cell rel part1 bg']"))
	        )
            #print('Element found!')
        except:
            print('Can\'t find element!')

    #login to the site
    def site_login(self, phone, password):
        try:
            phone_no = self.driver.find_element_by_xpath("//*[@placeholder='Mobile number']")
            passwrd = self.driver.find_element_by_xpath("//*[@placeholder='Password']")
            login = self.driver.find_element_by_xpath("//*[@class='login-btn']")
        except:
            print('Unable to locate login section')
        else:
            phone_no.send_keys(phone)
            passwrd.send_keys(password)
            login.click()
            time.sleep(5)
            try:
                close = self.driver.find_element_by_xpath(".//p[@class='close']")
                close.click()
            except:
                print('No Add to Homescreen Barner')
    
    #handle messages from client and execute
    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")

        connected = True
        while connected:
            try:
                msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            except:
                break
            if msg_length:
                start_time = time.time()
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                    sys.exit()
                    
                print(f"[{addr}] {msg}")
            
                self.strip_msg(msg)
            self.check_matches()
            selected = False
            for team in self.home_list:
                if self.similar(self.scorer, team) == True:
                    selected_team = team
                    index = self.home_list.index(team)
                    #print(index, self.away_score_list(index))
                    self.total_goals = int(self.total_goals) + int(self.away_score_list[index])
                    print(f'Total goals: {self.total_goals}')
                    selected = True
                    break

            if selected == False:
                for team in self.away_list:
                    if self.similar(self.scorer, team) == True:
                        selected_team = team
                        index = self.away_list.index(team)
                        #print(index, self.home_score_list(index))
                        self.total_goals = int(self.total_goals) + int(self.home_score_list[index])
                        print(f'Total goals: {self.total_goals}')
                        selected = True
                        break
            if selected:
                print(selected_team, self.total_goals)
                self.get_slip(selected_team, int(self.total_goals))
            else:
                print('Team is not available in live')

            print("--- %s seconds ---" % (time.time() - start_time))
            break
        conn.close()
    
    #strip received message
    def strip_msg(self, msg):
        half = msg.find(',')
        if half:
            scorer = (msg[: half ])
            total_goals = (msg[half + 1 :])
            self.scorer, self.total_goals = scorer, total_goals
        else:
            print('Incomplete message')
    
    #start the server
    def start(self):
        self.server.listen()
        print(f'[LISTENING] Server is listening on {self.SERVER}')
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            
    #check the available live matches on Mozzart live page
    def check_matches(self):
        self.home_list = []
        self.away_list = []
        self.score_list = []
        self.home_score_list = []
        self.away_score_list = []
        try:
            home_teams = self.driver.find_elements_by_xpath("//*[@class='font-cond home']")
            away_teams = self.driver.find_elements_by_xpath("//*[@class='font-cond visitor']")
            scores = self.driver.find_elements_by_xpath("//*[@class='score total']")
            
        except:
            print('Cannot find teams')
        else:
            for team in home_teams:
                self.home_list.append(team.text)
                self.home_list = self.home_list

            for team in away_teams:
                self.away_list.append(team.text)
                self.away_list = self.away_list
            
            for score in scores:
                self.score_list.append(score.text)
                home_score = score.text[:1]
                away_score = score.text[2:]
                self.home_score_list.append(home_score)
                self.away_score_list.append(away_score)

                    

            #for i in range(len(home_teams)):
            #    print(f'{home_list[i]} {home_score_list[i]} Vs. {away_score_list[i]} {away_list[i]}')

    #ascertain if selected team matches with teams on site
    def similar(self, a, b):
        similarity =  SequenceMatcher(None, a, b).ratio()
        if similarity > 0.6:
            return True
        else:
            return False

    #generate slip using given team and expected score      
    def get_slip(self, team, score):
        team_odd = False
        try:
            team_odd = self.driver.find_element_by_xpath(f".//div[@title='{team} will score goal number {score} in the match ']")
        except:
            try:
                team_odd = self.driver.find_element_by_xpath(f".//div[@title='{team.upper()} will score goal number {score} in the match ']")
            except:
                print('Bet suspended!')
        if team_odd:
            try:
                team_odd.click()
            except Exception as e:
                print(f'{e}')  
            self.place_bet()  

    #place the bet based on generated slip
    def place_bet(self):
        try:
            enter_stake = self.driver.find_element_by_xpath(".//input[@class='amount']")
            place_bet = WebDriverWait(self.driver, 3).until(
	            EC.element_to_be_clickable((By.ID, "pay-ticket-btn"))
	        )
        except:
            print('Unable to locate input')
        else:
            self.driver.execute_script("window.scrollTo(1210,720)")
            enter_stake.clear()
            enter_stake.send_keys(self.stake)
            place_bet.click()
            try:
                close = WebDriverWait(self.driver, 10).until(
	            EC.presence_of_element_located((By.XPATH, ".//button[@class='button close']"))
	            )
                close.click()
                print('Bet placed successfully!')
            except:
                print('Bet might not have been placed!')

    #run the program
    def run(self):
        self.get_site()
        self.site_login('0712897106', 'Vin2am@254')
        self.start()
        

if __name__ == '__main__':
    Mozzart().run()