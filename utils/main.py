import time
from celery import shared_task
import regex
import requests
from google.cloud import vision
import re
import requests
import json

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "utils/VARApp-500af3e88363.json"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "VARApp-500af3e88363.json"


def get_screenshot(tw_url):
    print("sssssssss")
    ss_token = 'Q76HQFG-HJ5MT8Y-KQTFTHN-MC9DY6K'
    fresh = True
    lazy_load = True
    retina = True
    url = f'https://shot.screenshotapi.net/screenshot?token={ss_token}&url={tw_url}&fresh={fresh}&lazy_load={lazy_load}&delay=2000&retina={retina}'

    res = requests.get(url)

    print(res.json()['screenshot'])
    print(res.status_code)
    return res.json()['screenshot']


def encode_image(image_path):
    with open(image_path, 'rb') as image:
        content = image.read()
        return content


def regex_text(pattern, text):
    text = str(text)
    try:
        pattern = re.compile(r'{}'.format(pattern))
        matches = re.search(pattern, text)

        return matches.group(1)
    except Exception as e:
        print(e)
        return ''

def regex_find_all(pattern, text):
    text = str(text)
    try:
        matches = regex.findall(r'{}'.format(pattern), text)
        return matches
    except Exception as e:
        print(e)
        return ''

def time_int(t):
    try:
        tf = t.split(':')[0]
    except:
        tf = None
    return tf


def get_live_result(text, match_id):
    print("getting live result...")
    # print(text)
    time = ''

    try:
        time_3 = regex_text('(\d+:\d+:\d+)', text)
        print(time_3)
        modified_text = text.replace(time_3, '')
        p_time = regex_text('(\d+:\d+)', modified_text)
        print(p_time)

        home_away_teams = regex_find_all('(?<![A-Z])[A-Z]{3}(?![A-Z])', text)
        home_team = home_away_teams[0]
        away_team = home_away_teams[1]
        print('home_team:', home_team)
        print('away_team:', away_team)
        result = regex_text('(\d+[-]\d+)', text)
        home_result = result.split('-')[0]
        away_result = result.split('-')[1]
        print('home_result:', home_result)
        print('away_result:', away_result)

        result = f'''screen= Live
time= {p_time}
home_team= {home_team}
home_result= {home_result}
away_team= {away_team}
away_result= {away_result}
'''
        print(result)
        tf = time_int(p_time)
        if tf:
            try:
                tfi = int(tf)
                if tfi and home_team and home_result and away_team and away_result:
                    with open('output/' + str(match_id) + '.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                else:
                    return 'MATCH_END'
            except Exception as e:
                print(e)
                return 'MATCH_END'

    except:
        return 'MATCH_END'

    return ''


def get_final_result(text, match_id):
    print("getting final result...")
    print("===============")
    print()
    print(text)
    print("===============")
    print()
    if 'CALIFICACIONES' in text:
        text = text.split('CALIFICACIONES')[0]
    if '¿CONTINUAR SERIE?' in text:
        text = text.split('¿CONTINUAR SERIE?')[0]

    print("===============")
    print()
    print(text)
    print("===============")
    print()

    time = ''
    home_team = ''
    home_result = ''
    away_team = ''
    away_result = ''

    try:
        time_3 = regex_text('(\d+:\d+:\d+)', text)
        print(time_3)
        modified_text = text.replace(time_3, '')
        p_time = regex_text('(\d+:\d+)', modified_text)
        print(p_time)
        for t in text.split('\n'):
            if t.isupper():
                if any(chr.isdigit() for chr in t):
                    if '-' in t:
                        home, away = t.split('-')
                        home = home.strip()
                        home_result = home[-1].strip()
                        home_team = home.replace(home_result, '').strip()
                        away = away.strip()
                        away_result = away[0].strip()
                        away_team = away.replace(away_result, '').strip()

        result = f'''screen= Final
time= {p_time}
home_team= {home_team}
home_result= {home_result}
away_team= {away_team}
away_result= {away_result}
'''
        print(result)
        tf = time_int(p_time)
        if tf:
            try:
                tfi = int(tf)
                if tfi and home_team and home_result and away_team and away_result:
                    with open('output/' + str(match_id) + '.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                else:
                    pass
            except:
                pass

    except:
        pass



gcloud_api_key = 'AIzaSyDRvI10uclo9uBnk5IzbfnEOlQV9_grCSM'
URL = f"https://vision.googleapis.com/v1/images:annotate?key={gcloud_api_key}"


def do_ocr(screenshot_url):
    print("doing ocr..")
    data = {
        "requests": [
            {
                'image': {'source': {'image_uri': screenshot_url}},
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION",
                        # other options: LABEL_DETECTION FACE_DETECTION LOGO_DETECTION CROP_HINTS WEB_DETECTION
                        # "maxResults": 10
                    }
                ]
            }
        ]
    }
    response = requests.post(URL, json=data)
    # return r.text

    # texts = response.json()['text_annotations'
    text = response.json()['responses'][0]['textAnnotations'][0]['description']
    print('ocr done')
    # print("===========================")
    # print(text)
    # print("===========================")
    return text


# text = do_ocr('https://screenshotapi-dot-net.storage.googleapis.com/m_twitch_tv_soy_mandrake_32bae28367be.png')
#
# get_final_result(text, '87657')






# counter = 0
# def start_tracking(tw_url, match_id):
#     global counter
#     for i in range(150):
#         ss_url = get_screenshot(tw_url)
#         print(ss_url)
#         text = do_ocr(ss_url)
#
#         if "¿CONTINUAR SERIE?" in text or "CALIFICACIONES" in text:
#             print("final")
#             get_final_result(text, match_id)
#             break
#         else:
#             print("live")
#             flag = get_live_result(text, match_id)
#             print("flag:", flag)
#             if flag == 'MATCH_END':
#                 counter += 1
#
#             print("counter:", counter)
#             if counter >= 3:
#                 break
#
#         time.sleep(5)
#
# start_tracking('https://www.twitch.tv/soy_mandrake', '123')