import requests
import yaml
from bs4 import BeautifulSoup
import os.path


class Didlogic:
    def __init__(self):
        self.s = requests.Session()
        config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
        self.email = config['didlogic']['email']
        self.password = config['didlogic']['password']

    def get_token_and_session(self):
        try:
            url = 'https://didlogic.com/'
            response = self.s.get(url)

            # get token
            html_text = response.text
            soup = BeautifulSoup(html_text, 'html.parser')
            csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

            # get session
            didlogic_sessions = response.cookies.get('didlogic_sessions')

            return csrf_token, didlogic_sessions

        except Exception as e:
            raise AssertionError(f'Failed to get the token and session ID: {e}')

    def login(self, csrf_token, didlogic_sessions):
        url = f'https://didlogic.com/session?email={self.email}&password={self.password}'
        headers = {
                   'X-Csrf-Token': csrf_token,
                   'cookie': f'didlogic_sessions={didlogic_sessions}'
        }

        response = self.s.post(url, headers=headers)
        if response.cookies.values():
            with open('session', 'w') as sf:
                sf.write(didlogic_sessions)
        else:
            raise AssertionError('Login failed')

    def refresh_session(self):
        csrf_token, didlogic_sessions = self.get_token_and_session()
        self.login(csrf_token, didlogic_sessions)

    @staticmethod
    def read_session():
        with open('session', 'r') as sf:
            didlogic_sessions = sf.read()
        return didlogic_sessions

    def get_balance(self):
        if not os.path.exists('session'):
            self.refresh_session()

        didlogic_sessions = self.read_session()

        url = 'https://didlogic.com/balance'
        headers = {'cookie': f'didlogic_sessions={didlogic_sessions};'}
        response = self.s.get(url, headers=headers)

        if '<html>' in response.text:
            self.refresh_session()
            didlogic_sessions = self.read_session()
            headers = {'cookie': f'didlogic_sessions={didlogic_sessions};'}
            response = self.s.get(url, headers=headers)

        try:
            balance = round(float(response.text.replace('"', ''))/100, 2)
            return balance

        except Exception as e:
            raise AssertionError(f'Failed to get the balance: {e}')

# dl = Didlogic()
# print(dl.get_balance())
