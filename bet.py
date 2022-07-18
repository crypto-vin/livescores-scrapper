import requests
import json

class Bet:
    def __init__(self):
        self.stake = '10'
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

    def livebet(self, live,s):
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
                index = 0 #TODO the index to be varying between 0--home and 2--away depending on which side there is a goal
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

    def check_live_bet(self, s):
        response = s.get('https://live.betika.com/v1/uo/matches?page=1&limit=1000&sub_type_id=1,186,340&sport=14&sort=1', headers=self.headers)
        response_text = json.loads(response.text)
        #print(response_text)

        data = response_text['data']
        lives = []
        for key in data:
            game = {}
            if key['home_team'] or key['away_team']== 'Pusamania':
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
            self.livebet(live,s)



    def run(self):
        #login and maintain the session
        with requests.Session() as s:
            response = s.post('https://api.betika.com/v1/login', headers=self.headers, json=self.json_data)
            response_text = response.text
            response_text = json.loads(response_text)
            #print(response_text)

            id = response_text['data']['user']['id']
            token = response_text['token']
            self.bet_data['stake'] = self.stake
            self.bet_data['profile_id'] = id
            self.bet_data['token'] = token
            with open('data.json', 'w') as f:
                json.dump(self.bet_data, f)

            self.check_live_bet(s)    

if __name__ == '__main__':
    Bet().run()    