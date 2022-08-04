#Created by Vincent Munyalo

from fileinput import close
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from difflib import SequenceMatcher
import socket
import sys
import threading
from datetime import datetime
import africastalking

class Mozzart:
    #initialize Mozzart class
    def __init__(self):
        #self.phone = input('Enter phone number: ')
        #self.password = input('Enter password: ')
        #self.stake = input('Enter stake: ')
        PATH = "C:\Program Files (x86)\chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
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
        self.stake = 500
        self.prev_msg = ''
        self.phone = '0712897106'
        self.password = 'Vin2am@254'
        self.bet_placed = False
        self.similarity = 0.00
        self.recipients = []
        self.possible_win = 0
        self.count = 1
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
                pass
    
    #handle messages from client and execute
    def handle_client(self, conn, addr):
        now = datetime.now().time().replace(microsecond=0).isoformat()
        connected = True
        if self.count % 5 == 0:
            try:
                self.cashout()
            except:
                cashout = False
        
        while connected:
            self.bet_placed = False
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
                if msg == self.prev_msg:
                    break
                
                print(f'\nFetched new data at {now}')
                print(f"New goal detected: {msg}")
            
                self.strip_msg(msg)
            self.check_matches()
            selected = False
            prev_similarity = 0.65
            for team in self.home_list:
                if self.similar(self.scorer, team) == True:
                    if self.similarity >= prev_similarity:
                        selected_team = team
                        index = self.home_list.index(team)
                        self.total_goals = int(self.total_goals) + int(self.away_score_list[index])
                        print(f'Goal number: {self.total_goals}')
                        selected = True
                        prev_similarity = self.similarity

            for team in self.away_list:
                if self.similar(self.scorer, team) == True:
                    if self.similarity >= prev_similarity:
                        selected_team = team
                        index = self.away_list.index(team)
                        self.total_goals = int(self.total_goals) + int(self.home_score_list[index])
                        print(f'Goal number: {self.total_goals}')
                        selected = True
                        prev_similarity = self.similarity

            if selected:
                print(selected_team, self.total_goals)
                self.get_slip(selected_team, int(self.total_goals))
                if self.bet_placed:
                    self.send_text(selected_team, self.total_goals, self.possible_win)
            else:
                print('Team is not available in Mozzart livebets')

            print("--- %s seconds ---" % (time.time() - start_time))
            
            if self.count % 500 == 0:
                self.get_balance()
                threshold = self.stake * 10    

            self.prev_msg = msg
            break
        conn.close()
        try:
            login = self.driver.find_element_by_xpath("//*[@class='login-btn']")
        except:
            logged_in = True
        else:
            phone_no = self.driver.find_element_by_xpath("//*[@placeholder='Mobile number']")
            passwrd = self.driver.find_element_by_xpath("//*[@placeholder='Password']")
            phone_no.clear()
            passwrd.clear()
            phone_no.send_keys(self.phone)
            passwrd.send_keys(self.password)
            login.click()
            print('Logged in again')

        self.count += 1
    
    #check balance
    def get_balance(self):
        try:
            money = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='flex column betting-balance']//p[@class='money']"))
            )
            amount_available = money.text
            print(f'Balance: {amount_available}')
            self.stake = float(amount_available) / 4
        except:
            print('Unable to retrieve balance')
        
    
    #strip received message
    def strip_msg(self, msg):
        half = msg.find(',')
        if half:
            scorer = (msg[: half ])
            total_goals = (msg[half + 1 :])
            self.scorer, self.total_goals = scorer, total_goals
        else:
            print('Incomplete message')
            self.scorer, self.total_goals = 'Null', 0
    
    #send text message 
    def send_text(self, team, goals, possible_win):
        num = str('+254' + self.phone[1:])
        self.recipients.append(num)
        username = 'algobet254'
        api_key='ca3772ca14af112280ae148c3cd969f46efc91eac893b0f544f722613d077bda'
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        message = f'Algobet has placed a bet successfully! {team} to score goal no. {goals}. Possible win: Kshs {possible_win}'
        try:
            response = sms.send(message, self.recipients, None)
        except Exception as e:
            print (f'Couldn\'t send sms: {e}')

    #start the server
    def start(self):
        self.server.listen()
        print(f'[LISTENING] Server is listening on {self.SERVER}')
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            thread.join()
            
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


    #ascertain if selected team matches with teams on site
    def similar(self, a, b):
        similarity =  SequenceMatcher(None, a, b).ratio()
        self.similarity = similarity
        if similarity > 0.65:
            return True
        else:
            return False

    #generate slip using selected team and expected score      
    def get_slip(self, team, score):
        team_odd = False
        try:
            team_odd = self.driver.find_element_by_xpath(f".//div[@title='{team} will score goal number {score} in the match ']")
        except:
            try:
                team_odd = self.driver.find_element_by_xpath(f".//div[@title='{team.upper()} will score goal number {score} in the match ']")
            except:
                print('This bet has been suspended!')
        if team_odd:
            try:
                team_odd.click()
            except Exception as e:
                print(f'{e}')  
            self.place_bet(self.stake)  

    #place the bet based on generated slip
    def place_bet(self, stake):
        try:
            enter_stake = self.driver.find_element_by_xpath(".//input[@class='amount']")
            place_bet = WebDriverWait(self.driver, 3).until(
	            EC.element_to_be_clickable((By.ID, "pay-ticket-btn"))
	        )
        except:
            print('Unable to locate input')
        else:
            try:
                button_index = 0
                close_buttons = self.driver.find_elements_by_xpath(".//div[@class='close-button']")
                for button in close_buttons:
                    if button_index > 0:
                        button.click()
                    button_index += 1
            except:
                advert = False

            self.driver.execute_script("window.scrollTo(1210,720)")
            enter_stake.clear()
            enter_stake.send_keys(stake)
            payouts = self.driver.find_elements_by_xpath(".//p[@class='right payout']")
            payout_index = 0
            for payout in payouts:
                if payout_index == 1:
                    self.possible_win = payout.text
                payout_index += 1
            place_bet.click()
            try:
                close = WebDriverWait(self.driver, 6).until(
	                EC.presence_of_element_located((By.XPATH, ".//button[@class='button close']"))
	            )
                close.click()
                    
            except Exception as e:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//button[@class='button changes']"))
                    ).click()
                except:
                    print(f'Bet might not have been placed!: {e}')
                    self.driver.get(self.url)
            else:
                print(f'Bet placed successfully!')
                self.bet_placed = True
            
    #enter cashout threshold
    def cashout(self):
        cashout = self.driver.find_element_by_xpath(".//p[@class='header-text']//span[@class='counter']")
        cashouts = int(cashout.text)
        if cashouts != 0:
            cashout_status = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "cashout-value"))
                    )
            cashout_value = float(cashout_status.text)
            cashout_threshold = self.stake * 0.75
            if cashout_value < cashout_threshold:
                cashout_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, ".//div[@class='buttonCO']"))
                )
                cashout_button.click()
                print(f'Cashed out Kshs {cashout_value}')
                

    #withdraw if amount given exceeds 10 times the stake
    def withdraw(self, amount):
        try:
            self.driver.find_element_by_xpath(".//div[@class='flex column betting-balance']").click()
            time.sleep(10)
        except:
            print('Can\'t access balance page')
        else:
            try:
                options = WebDriverWait(self.driver, 20).until(
	                EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='nav-item']"))
	            )
                index = 0
                for option in options:
                    if index == 2:
                        option.click()
                        break
                    else:
                        index += 1
            except:
                print('The withdrawal link is unclickable')
            else:
                input_box = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, ".//div[@class='input-group']//input[@type='text']"))
                )
                input_box.click()
                input_box.send_keys(amount)
                try:
                    self.driver.find_element_by_xpath(".//div[@class='button-holder']//button[@id='pay-btn-mpesa']").click()
                except Exception as err:
                    print('Unable to withdraw: ' + err)
                else:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[@class='close-popup']"))
                    ).click()
                    print('Withdrawal successful')
                    time.sleep(5)

            finally:
                self.driver.get(self.url)

    #run the program
    def run(self):
        self.get_site()
        self.site_login(self.phone, self.password)
        self.start()
        

if __name__ == '__main__':
    Mozzart().run()