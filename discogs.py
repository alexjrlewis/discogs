"""."""

from __future__ import annotations
import datetime
import pickle
import requests
import sys
import time
from typing import Dict, List
import numpy as np
import pandas as pd

old_to_new = {
    # 'Label': 'label',
    'Have': 'n_have',
    'Want': 'n_want',
    'Avg Rating': 'rating',
    'Ratings': 'n_ratings',
    'Last Sold': 'last_sold',
    'Lowest': 'price_lowest',
    'Highest': 'price_highest',
    'Median': 'price_median'}

def extract_number(string):
    """
    Args:
        string:
    Returns:
    """
    try:
        whitelist = set('0123456789.')
        answer = ''.join([s for s in string if s in whitelist])
        median = answer
    except:
        median = np.nan
    return median

def _get(text, column):
    """
    Args:
        text:
        column:
    Returns:
    """
    value = ''
    # if column in ['Labl]:
    if column in ['Have', 'Want']:
        s_1 = f'<h4>{column}:</h4>'
        s_2 = '</a>'
        s_3 = '">'
        tmp_1 = text.split(s_1)[1]
        tmp_2 = tmp_1.split(s_2)[0]
        tmp_3 = tmp_2.split(s_3)[1]
        value = extract_number(tmp_3)
    elif column in ['Ratings', 'Avg Rating']:
        if column == 'Ratings':
            _class = 'count'
        else:
            _class = 'value'
        s_1 = f'<span class="rating_{_class}">'
        s_2 = '</span>'
        tmp_1 = text.split(s_1)[1]
        tmp_2 = tmp_1.split(s_2)[0]
        value = extract_number(tmp_2)
    elif column in ['Last Sold']:
        s_1 = f'<h4>{column}:</h4>'
        s_2 = '</a>'
        s_3 = '">'
        tmp_1 = text.split(s_1)[1]
        tmp_2 = tmp_1.split(s_2)[0]
        tmp_3 = tmp_2.split(s_3)[1]
        try:
            value = f'{pd.Timestamp(tmp_3).date()}'
        except:
            value = f'{pd.Timestamp(None)}'
    elif column in ['Lowest', 'Highest', 'Median']:
        s_1 = f'<h4>{column}:</h4>'
        s_2 = '</li>'
        tmp_1 = text.split(s_1)[1]
        tmp_2 = tmp_1.split(s_2)[0]
        value = extract_number(tmp_2)
    return value

def get(text: str):
    """
    """
    data = {}
    for k, v in old_to_new.items():
        data[v] = _get(text, k)
    return data

def get_release_data(release):
    """
    Args:
        release:
    Returns:
        ...
    """
    url = f'https://api.discogs.com/releases/{release}'
    r = requests.get(url)
    uri = r.json()['uri']
    r = requests.get(f'{uri}')
    text = r.text
    data = get(text)
    return data

def main():
    """
    """
    # filename = './io/classical.csv'
    # filename = './io/alex-soundtracks.csv'
    filename = './io/alex-10-inch.csv'
    # filename = './io/alex-jazz.csv'
    _df = pd.read_csv(filename)
    _df['release'] = [url.split('release/')[1] for url in _df['url']]
    df = pd.DataFrame(columns=old_to_new.values())
    for index, release in enumerate(_df['release']):
        data = get_release_data(release)
        data['release_id'] = release
        data['release_url'] = _df.loc[index, 'url']
        df = df.append(data, ignore_index=True)
        print(data)
        time.sleep(1.0)
    df['last_updated'] = f'{pd.Timestamp.today()}'
    output_filename = filename.replace('.csv', '--discogs-info.csv')
    df.to_csv(output_filename, index=False)
    print(df)

if __name__ == '__main__':
    main()

