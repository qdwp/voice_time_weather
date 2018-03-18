# -*- coding: utf-8 -*-
#!/usr/bin/env python


import os
import time
import json
import requests
import datetime
import schedule
import threading
from voicetools import BaiduVoice


API_KEY = ''            # 百度开发者 API_KEY
SECRET_KEY= ''          # 百度开发者 SECRET_KEY
BAIDU_AK = ''           # 百度地图ak BAIDU_AK

CURRENT_PATH = os.getcwd()

SYS_VOICE_PATH = os.path.join(CURRENT_PATH, 'sys_voice')
SYS_VOICE_NET_ERROR = os.path.join(SYS_VOICE_PATH, 'sys_net_error.mp3')
SYS_VOICE_QUERY_ERROR = os.path.join(SYS_VOICE_PATH, 'sys_failed.mp3')
SYS_VOICE_STS_ERROR = os.path.join(SYS_VOICE_PATH, 'sys_error.mp3')

EXPORT_VOICE_PATH = os.path.join(CURRENT_PATH, 'export_voice')

MYLOCATION = u'杨浦区'
WEATHER_IN_LOCATION = u'http://api.map.baidu.com/telematics/v3/weather?location={0}&output=json&ak={1}'.format(MYLOCATION, BAIDU_AK)


def check_net_connect():
    """ 检查网络连接 """
    _code = os.system('ping www.baidu.com -c 1')
    if _code != 0:
        print('network connect failed')
        return False
    else:
        return True


def get_current_time():
    """ 
    整点报时
    格式化成2016-03-20 11:45:39形式
    return 格式化时间, 秒级时间戳
    """
    _localtime = time.localtime()
    # return time.strftime("%Y-%m-%d %H:%M:%S", _localtime), int(time.mktime(_localtime))
    return time.strftime("%Y-%m-%d %H:%M", _localtime), int(time.mktime(_localtime))

def export_time_audio():
    """
    导出当前时间语音文件
    """
    if not check_net_connect():
        os.system('play {0}'.format(SYS_VOICE_NET_ERROR))
        return False, None
    baidu_token = BaiduVoice.get_baidu_token(API_KEY, SECRET_KEY)
    voice_operator = BaiduVoice(baidu_token['access_token'])

    time_string, timestamp = get_current_time()
    time_voice = voice_operator.tts('叮咚，当前时间。{}'.format(time_string))

    export_path = os.path.join(EXPORT_VOICE_PATH,  "{}_time.mp3".format(timestamp))
    with open(export_path, 'wb') as export:
        export.write(time_voice)

    return True, export_path


def get_todays_weather():
    """
    查询当天天气情况
    """
    responce = requests.get(WEATHER_IN_LOCATION)
    if responce.ok and responce.status_code == 200:
        _result = json.loads(responce.content.decode("utf-8"))
        if _result['status'] == "success":
            current_city = _result['results'][0]['currentCity']
            current_data = _result['results'][0]['index']
            weather_data = _result['results'][0]['weather_data']

            data_string = "叮咚，实时天气信息。{0}。{1}。{2}{3}".format(
                    "{0}".format(current_city.encode('utf-8')),
                    "{0}。{1}。{2}。{3}".format(
                        weather_data[0]['date'].encode('utf-8'),
                        weather_data[0]['weather'].encode('utf-8'),
                        weather_data[0]['temperature'].encode('utf-8'),
                        weather_data[0]['wind'].encode('utf-8')
                        ),
                    "{0}。{1}。{2}".format(
                        current_data[0]['tipt'].encode('utf-8'),
                        current_data[0]['zs'].encode('utf-8'),
                        current_data[0]['des'].encode('utf-8')
                        ),
                    "{0}。{1}。{2}".format(
                        current_data[2]['tipt'].encode('utf-8'),
                        current_data[2]['zs'].encode('utf-8'),
                        current_data[2]['des'].encode('utf-8')
                        ),
                )
            print(data_string)
            export_path = os.path.join(EXPORT_VOICE_PATH,  u"{0}_weather.mp3".format(_result['date'].encode('utf-8')))

            baidu_token = BaiduVoice.get_baidu_token(API_KEY, SECRET_KEY)
            voice_operator = BaiduVoice(baidu_token['access_token'])

            with open(export_path, 'wb') as export:
                export.write(voice_operator.tts(data_string))
                return True, export_path
        else:
            os.system('play {0}'.format(SYS_VOICE_QUERY_ERROR))
            return False, None
    else:
        os.system('play {0}'.format(SYS_VOICE_QUERY_ERROR))
        return False, None


def play_time_audio():
    success, audio_path = export_time_audio()
    print(success, audio_path)
    if success:
        os.system("play {}".format(audio_path))
        os.remove(audio_path) if os.path.exists(audio_path) else None

def play_weather_audio():
    success, audio_path = get_todays_weather()
    if success:
        os.system("play {}".format(audio_path))
        os.remove(audio_path) if os.path.exists(audio_path) else None

def time_audio_task():
    print(get_current_time()[0])
    threading.Thread(target=play_time_audio).start()

def todays_weather_task():
    print(get_current_time()[0])
    threading.Thread(target=play_weather_audio).start()


if __name__ == '__main__':

    # play_time_audio()

    # play_weather_audio()

    schedule.every().day.at('8:00').do(time_audio_task)
    schedule.every().day.at('8:10').do(time_audio_task)
    schedule.every().day.at('22:00').do(time_audio_task)
    schedule.every().day.at('23:00').do(time_audio_task)
    schedule.every().day.at('23:30').do(time_audio_task)
    schedule.every().day.at('8:20').do(todays_weather_task)

    while True:
        schedule.run_pending()
        time.sleep(1)




