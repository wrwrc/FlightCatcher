from hashlib import sha1
import hmac
from datetime import datetime
import base64
import sys
import requests

class Client(object):
    def __init__(self, app_id, app_key):
        self._app_id = app_id
        self._app_key = app_key

    def _get_auth_header(self):
        xdate = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        hashed = hmac.new(self._app_key.encode('UTF8'), ('x-date: ' + xdate).encode('UTF8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()
        authorization = f'hmac username="{self._app_id}",algorithm="hmac-sha1",headers="x-date",signature="{signature}"'

        return {
            'Authorization': authorization,
            'x-date': xdate,
            'Accept - Encoding': 'gzip'
        }

    def get(self, rel_path):
        headers = self._get_auth_header()
        path = 'http://ptx.transportdata.tw/MOTC' +\
                rel_path +\
                ('&' if '?' in rel_path else '?') +\
                '$format=JSON'
        resp = requests.get(path, headers = headers)
        resp.raise_for_status()
        return resp.json()

if __name__ == '__main__':
    app_id = input('app id = ')
    app_key = input('app key = ')
    client = Client(app_id, app_key)
    rel_path = input('api = ')
    result = client.get(rel_path)
    print(result)

