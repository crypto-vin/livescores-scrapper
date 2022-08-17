from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import socket
import time


class Flashscore():
    def __init__(self):
        self.bet_list = []
        self.message = ''
        self.total_goals = 0
        self.team = ''
        self.oponent = ''

        PATH="C:\Program Files (x86)\chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', {'credentials_enable_service': False,
                                                         'profile': {'password_manager_enabled': False}})
        self.browser = webdriver.Chrome(executable_path = PATH, options=chrome_options)

    def run(self):
        self.launch_flashscore()
        self.live_scanning()

    def launch_flashscore(self):
        self.browser.get("https://www.flashscore.com/")
        # accept cookies
        try:
            accept_cookies = WebDriverWait(self.browser, 300).until(EC.element_to_be_clickable((By.ID,
                                                                                                "onetrust-accept-btn-handler")))
            accept_cookies.click()
        except:
            pass

        time.sleep(4)

        # click lIVE, likely to break if HTML was changed
        live = self.browser.find_element(By.XPATH,
                                         "/html/body/div[6]/div[1]/div/div[1]/div[2]/div[4]/div[2]/div/div[1]/div[1]/div[2]/div[2]")
        live.click()
        print('Searching for a goal...')

    def has_xpath(self, xpath, el):
        try:
            el.find_element(By.XPATH, xpath)
            return True
        except:
            return False

    def process_message(self):
        msg = f'{self.team},{self.total_goals}-{self.oponent}'
        if msg not in self.bet_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "127.0.0.1"
            port = 5080
            HEADER = 64
            FORMAT = 'utf-8'
            sock.connect((host, port))
            try:
                message = msg.encode(FORMAT)
                msg_length = len(message)
                send_length = str(msg_length).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length))
                sock.send(send_length)
                sock.send(message)
                # send message only when it was not sent before
                self.bet_list.append(msg)
            except:
                print('message not sent')

            print(f'{self.team}, goal number {self.total_goals} against {self.oponent}')
        if len(self.bet_list) > 10:
            self.bet_list.pop(0)

    def live_scanning(self):
        # continuous looping through flashscore
        while True:

            try:
                element = WebDriverWait(self.browser, 1000).until(
                    EC.presence_of_element_located((By.XPATH, './/div[@title="Click for match detail!"]')))

                elements = self.browser.find_elements(By.XPATH, './/div[@title="Click for match detail!"]')
                #print('Live games are ' + str(len(elements)))

            except:
                print('no live games')
                pass

            else:
                for el in elements:
                    try:
                        # check for GOAL
                        el.find_element(By.XPATH, './/div[@class="highlightMsg fontBold"]')
                    except:
                        # no GOAL, continue looping
                        pass
                    else:
                        # home team has scored
                        xpath1 = ('.//div[@class="event__participant event__participant--home highlighted"]')
                        if self.has_xpath(xpath1, el):
                            try:
                            #if el.find_element(By.XPATH, './/div[@class="event__participant event__participant--home highlighted"]'):
                                # only pick the team name, first 10 strings
                                home_team = el.find_element(By.XPATH, './/div[@class="event__participant event__participant--home highlighted"]').text
                                away_team = el.find_element(By.XPATH, './/div[@class="event__participant event__participant--away"]').text
                                self.team = ''.join(home_team.replace('GOAL', '').splitlines())
                                self.oponent = away_team

                                home_score = int((el.find_element(By.XPATH, './/div[@class="event__score event__score--home highlighted"]')).text)
                                away_score = int((el.find_element(By.XPATH, './/div[@class="event__score event__score--away"]')).text)

                                self.total_goals = home_score + away_score

                                self.process_message()
                            except:
                                pass

                        # away team has scored
                        xpath2 = ('.//div[@class="event__participant event__participant--away highlighted"]')
                        if self.has_xpath(xpath2, el):
                            try:
                                away_team = el.find_element(By.XPATH, './/div[@class="event__participant event__participant--away highlighted"]').text
                                home_team = el.find_element(By.XPATH, './/div[@class="event__participant event__participant--home"]').text
                                self.team = ''.join(away_team.replace('GOAL', '').splitlines())
                                self.oponent = home_team
                                
                                home_score = int((el.find_element(By.XPATH, './/div[@class="event__score event__score--home"]')).text)
                                away_score = int((el.find_element(By.XPATH, './/div[@class="event__score event__score--away highlighted"]')).text)

                                self.total_goals = home_score + away_score

                                self.process_message()
                            except:
                                pass

if __name__ == "__main__":
    app = Flashscore()
    app.run()
