from hashlib import sha1
import hmac
from datetime import datetime
import base64
import sys
import asyncio
import aiohttp

class Client(object):
    def __init__(self, app_id, app_key):
        self._app_id = app_id
        self._app_key = app_key

    def _get_auth_header(self):
        xdate = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        hashed = hmac.new(
            self._app_key.encode('UTF8'),
            ('x-date: ' + xdate).encode('UTF8'),
            sha1)
        signature = base64.b64encode(hashed.digest()).decode()
        authorization = f'hmac username="{self._app_id}",' +\
            f'algorithm="hmac-sha1",headers="x-date",signature="{signature}"'

        return {
            'Authorization': authorization,
            'x-date': xdate,
            'Accept - Encoding': 'gzip'
        }

    async def get(self, rel_path):
        headers = self._get_auth_header()
        path = 'http://ptx.transportdata.tw/MOTC' + rel_path +\
                ('&' if '?' in rel_path else '?') + '$format=JSON'

        async with aiohttp.ClientSession(
                    headers=headers,
                    raise_for_status=True
                ) as session:
            async with session.get(path, raise_for_status=False) as resp:
                return await resp.json()

async def main():
    app_id = input('app id = ')
    app_key = input('app key = ')

    client = Client(app_id, app_key)

    rel_path = input('api = ')
    result = await client.get(rel_path)

    print(result)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()