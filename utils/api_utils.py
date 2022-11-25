import json 
import requests

import logging
import os


apikey = 'RGAPI-4e3b2309-04f5-4734-941c-12717aa3101b'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": apikey
}

def generate_url(url_base, suffix):
    return url_base.strip('/') + '/' + suffix.strip('/')


def retrieve_data(log, url, is_list=False):
    log.info(f'sending request to {url}')
    response = requests.get(url, headers=headers)
    log.info(f'status_code: {response.status_code}')
    if response.status_code == 200:
        if is_list == True:
            data = eval(response.text)
        else:
            data = json.loads(response.text)
        return data 
    else:
        log.info(f'request failed with status {response.status_code}')



url_base = 'https://br1.api.riotgames.com/'
url_base_americas = 'https://americas.api.riotgames.com/'



