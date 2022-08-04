from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import africastalking

class Withdraw:
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
        self.phone = '0712897106'
        self.password = 'Vin2am@254'
        self.stake = 10

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
        
    def get_balance(self):
        try:
            money = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='flex column betting-balance']//p[@class='money']"))
            )
            amount_available = money.text
            print(f'Balance: {amount_available}')
        except:
            print('Unable to retrieve balance')
        else:
            threshold = self.stake * 10
            if float(amount_available) > threshold:
                print('Proceeding to withdraw')

    #enter cashout threshold
    def cashout(self):
        try:
            cashout = self.driver.find_element_by_xpath(".//p[@class='header-text']")
        except:
            print('No cashouts available')
        else:
            cashout_status = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.ID, "cashout-value"))
                    )
            cashout_value = float(cashout_status.text)
            cashout_threshold = self.stake * 0.8
            if cashout_value < cashout_threshold:
                cashout_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, ".//div[@class='buttonCO']"))
                )
                cashout_button.click()
                print(f'Cashed out Kshs {cashout_value}')
    
    #withdraw if amount exceeds 10 times the stake
    def withdraw(self, amount):
        time.sleep(10)
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
                try:
                    input_box = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, ".//div[@class='input-group']//input[@type='text']"))
                    )
                    input_box.click()
                    input_box.send_keys(amount)
                except Exception as err:
                    print(f'cant locate input box: {err}')
                try:
                    to_mpesa = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//div[@class='button-holder']//button[@id='pay-btn-mpesa']"))
                    )
                    to_mpesa.click()

                except Exception as e:
                    print('cannot locate mpesa button: ' + e)

                else:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[@class='close-popup']"))
                    ).click()
                    print('Withdrawal successful')
                    time.sleep(5)

            finally:
                self.driver.get(self.url)

    def send_text(self, team, goals, win):
        num = str('+254' + self.phone[1:])
        self.recipients = ['+254712897106']
        username = 'algobet254'
        api_key='ca3772ca14af112280ae148c3cd969f46efc91eac893b0f544f722613d077bda'
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        message = f'Bet placed successfully! {team} to score goal number {goals}. Possible win: Kshs {win}'
        try:
            response = sms.send(message, self.recipients, None)
        except Exception as e:
            print (f'Couldn\'t send sms: {e}')
    
    def run(self):
        #self.get_site()
        #self.site_login(self.phone, self.password)
        #self.get_balance()
        #self.cashout()
        #self.withdraw(200)
        self.send_text('Arsenal', 3, 1435 )
            
if __name__ == '__main__':
    Withdraw().run()