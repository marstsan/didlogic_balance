import requests
import yaml
from .loginEncrypt import passwordEncryption


class CinnoxTool:
    def __init__(self):
        self.s = requests.Session()
        self.config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)

        self.edge_server = 'https://hkpd-ed-aws.cx.cinnox.com'
        self.service_id = self.get_service_id(self.config['notification']['service'])
        self.username = self.config['notification']['account']
        self.password = self.config['notification']['password']
        self.room_id_list = self.config['notification']['room_id']

        self.eid, self.token = self.get_eid_token(self.edge_server, self.service_id, self.username, self.password)

    def get_service_id(self, service):
        response = self.s.get(f'{self.edge_server}/m800-csd/v2/services/{service.split("https://")[1]}').json()['result']

        return response['serviceId']

    def get_eid_token(self, edge_server, service_id, username, password):
        encrypt_password, rnd = passwordEncryption(password)
        url = f'{edge_server}/auth/v1/service/{service_id}/users/token'
        headers = {'accept': 'application/json', 'content-type': 'application/json;charset=UTF-8'}
        body = {'username': username, 'password': encrypt_password, 'grant_type': 'password', 'challenge': {'type': 'mcpwv3', 'rand': rnd}}
        response = self.s.post(url, headers=headers, json=body)
        eid = response.json()['result']['eid']
        token = response.json()['result']['access_token']

        return eid, token

    def send_notification(self, text):
        room_name = 'jack_test_space'
        eid, token = self.get_eid_token(self.edge_server, self.service_id, self.username, self.password)

        results = {}
        for room_id in self.room_id_list:
            url = f'{self.edge_server}/im/v1/im/events/rooms/{room_id}/message'
            headers = {'x-m800-eid': eid, 'authorization': f'bearer {token}',
                       'x-m800-dp-sendername': 'Didlogic Balance Monitor',
                       'x-m800-dp-styledtext': 'Didlogic Balance Monitor',
                       'x-m800-dp-roomname': room_name
                       }
            body = {'type': 1, 'text': f'{text}'}

            response = self.s.post(url, headers=headers, json=body)

            results[room_id] = response.json()

        return results
    