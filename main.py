import time
import datetime
import json
import requests
# from data import webhook_url, users, payload


def get_problems_json():
    problems_json_url = "https://kenkoooo.com/atcoder/resources/problem-models.json"
    print("---過去問データを取得---")
    try:
        responce = requests.get(problems_json_url)
        responce.raise_for_status()  # check the status code
        print(f"status: {responce.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        return -1
    problems_json_text = responce.text
    problems_json_data = json.loads(problems_json_text)
    print("------------------------\n")
    return problems_json_data


def post_to_discord(msg):
    global payload
    global webhook_url
    payload["content"] = msg
    try:
        r = requests.post(webhook_url, data=payload)
        r.raise_for_status() # check the status code
        print(f"status: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")


def DC_converter(num): #difficulty to color converter
    colors = [':white_heart:', ':brown_heart:', ':green_heart:', ':sweat_drops:' ':blue_heart:' ,':yellow_heart:', ':orange_heart:', 'heart']
    key = min(len(colors) - 1, max(0, num // 400))
    return colors[key]


def check_submission(usr, time):
    print(f"--{usr}の提出をチェック--")
    global problems_json_data
    global webhook_url
    global payload
    user_url = f"https://kenkoooo.com/atcoder/atcoder-api/results?user={usr}&from_second={time}"
    l_AC_time = time
    pad = "-" * len(usr)

    # get usr's submission data
    try:
        responce = requests.get(user_url)
        responce.raise_for_status()  # check the status code
        print(f"status: {responce.status_code}")
        res = responce.json()
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")

    # check usr's submission
    for result in res:
        if result['epoch_second'] > time and result['result'] == "AC":      # find a new AC
            l_AC_time = max(l_AC_time, result['epoch_second'])              # update latest AC time
            ac_datetime = datetime.datetime.fromtimestamp(result['epoch_second'])
            problem_id = result['problem_id']
            submit_url = f"https://atcoder.jp/contests/{result['contest_id']}/submissions/{result['id']}"
            try:
                diff = problems_json_data[problem_id]['difficulty']
                diff = max(0, diff)
                color = DC_converter(diff)
            except KeyError:
                diff = "???"
                color = "???"
            # notify
            message = f"**{usr}**が*{problem_id}*をACしました！({ac_datetime})\rDiff: {color}\r{submit_url}"
            print(message)
            post_to_discord(message)

    if l_AC_time == time: print("No sub")
    print(f"{pad}--------------------\n")
    return l_AC_time


if __name__ == '__main__':
    webhook_url = "hogehoge"
    users = ['misonikomipan']
    payload = {
                    "username": "ACnotifier",
                    "avatar_url": "https://www.ad-c.or.jp/images/logo_l_new.png",
                    "content": "test"
                    }
    message = "チェック開始!"
    print(message)
    post_to_discord(message)
    latest_AC_time = int(time.time()) - 300 # before 10 minutes (initial value) 
    try:
        while 1: # main loop
            before = latest_AC_time
            problems_json_data = get_problems_json()
            time.sleep(5)
            for user_name in users:
                ac_time = check_submission(user_name, before)
                latest_AC_time = max(latest_AC_time, ac_time)
                time.sleep(2)
        
    except KeyboardInterrupt:
        # Ctrl-C
        message = '**動作を停止したよ！**(KEYBOARD INTERRUPT)'
        print(message)
        post_to_discord(message)
        exit()