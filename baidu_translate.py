import requests
import random
import json
from hashlib import md5
from typing import Union, List


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


class baidu_translate:
    def __init__(self, app_id: str = '000', app_key: str = '000'):
        self.app_id = app_id
        self.app_key = app_key

        self.from_lang = 'en'
        self.to_lang = 'zh'

        endpoint = 'https://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        self.url = endpoint + path

    def translate(self, text: Union[str, List[str]], **kwargs):
        if type(text) == list:
            text = '\n'.join(text)
        salt = random.randint(32768, 65536)
        sign = make_md5(self.app_id + text + str(salt) + self.app_key)

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.app_id, 'q': text, 'from': self.from_lang, 'to': self.to_lang, 'salt': salt, 'sign': sign}

        result_json = requests.post(self.url, params=payload, headers=headers)
        result = result_json.json()

        return result


if __name__ == '__main__':
    test_text = ['And go where?',
                 'Anywhere.Your room.My house.That new apartment you got me.',
                 'Am I truly the one you wish to leave here with?',
                 '''In the sense that I'm in love with you or something?No.''',
                 '''But in the sense that I feel eerily safe whenever I'm with you,yes.I want you by my side until this all boils over.''',
                 '''And if it never does,will we remain together forever?''',
                 '''I {i} should {/i} say that I feel a little relieved to find out that {i} this {/i} is why you’ve been hanging out with Kaori lately, though. She’s really pretty and I got jealous and...I’m sorry.''']

    mt = baidu_translate()
    result = mt.translate(test_text)
    print(json.dumps(result, indent=4, ensure_ascii=False))
