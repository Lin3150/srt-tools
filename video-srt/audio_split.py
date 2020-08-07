#!/usr/bin/env python
# -*-coding:utf-8 -*-

import os
import pydub
from moviepy.editor import *
import time
import sys
import json
import base64
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from urllib.parse import urlencode
timer = time.perf_counter
from restruct import batpro

global filepath

APP_ID = '18773537'
API_KEY = 'FTaOGRzFXBKOfAwrr9GdHp3p'
SECRET_KEY = 'ID2tB2TmvV8B22lw7RNB6NXH8pscl9eC'
FORMAT = 'wav'
CUID = '123456PYTHON'
DEV_PID = 1737
RATE = 16000
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'
TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'

class DemoError(Exception):
    pass

#官方文档token获取
def fetch_token(): 
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode( 'utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except HTTPError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        print(SCOPE)
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

#官方文档接口输入规范
def audio2text(wavsample): 
    length = len(wavsample)
    if length == 0:
        raise DemoError('file length read 0 bytes' )
    speech = base64.b64encode(wavsample)
    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
                  'format': FORMAT,
                  'rate': RATE,
                  'token': token,
                  'cuid': CUID,
                  'channel': 1,
                  'speech': speech,
                  'len': length
                  }
    post_data = json.dumps(params, sort_keys=False)
     # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        print ("Request time cost %f" % (timer() - begin))
        result_str = json.loads(result_str)
        try:
            result_str = result_str['result'][0]
        except:
            result_str = ' '
    except HTTPError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = ''  
    return result_str
    
#批处理 输入文件夹 收集文件夹内所有文件名
#文件名不带路径带后缀.mp4
def batprocess(filepath):
    filename = os.listdir(filepath)
    for i in filename:
        if os.path.splitext(i)[1] == '.mp4':
            oneprocess(i)

#对单个文件进行处理并创建文件夹
#处理步骤1.提取音频2.音频分块3.生成.srt
def oneprocess(filename):
    if not os.path.exists(filepath + '\\towav'):
        os.mkdir(filepath + '\\towav')
    vedio2wav(filename)
    if not os.path.exists(filepath + '\\process\\'):  
        os.mkdir(filepath + '\\process\\')    
    if not os.path.exists(filepath + '\\process\\' + filename[:-4] ):  
        os.mkdir(filepath + '\\process\\' + filename[:-4] )
    wavechunk(filename)

#生成音频      
def vedio2wav(filename):
    vedio = VideoFileClip(filepath + '\\' + filename)
    audio = vedio.audio
    wavfilepath = filepath + '\\towav\\' + filename[:-4] + '.wav'
    audio.write_audiofile(wavfilepath)
    
#音频分块并生成.srt文件    
def wavechunk(filename, min_silence_len=430, silence_thresh=-34):
    #根据接口默认音频格式
    filename = filename[:-4]
    wavfilepath = filepath + '\\towav\\' + filename + '.wav'
    sound = pydub.AudioSegment.from_wav(wavfilepath)
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    #音频分块 参数根据音频质量调整
    pieces,start_t,end_t = pydub.silence.split_on_silence(sound, min_silence_len, silence_thresh)
    #分块生成音频列表，音频块开始时间列表，结束时间列表
    #将音频导出文件夹，方面提取。也可以不导出直接在程序内将音频传入接口
    #各有优劣，这边采取导出到本地文件夹，将音频信息按顺序导出
    gotwave(pieces, filename)
    #读取文件夹中的音频，根据
    with open(filepath + '\\' + filename + '.srt', 'w') as f:
        for inx,val in enumerate(pieces):
            #读取音频文件
            #wav = get_file_content(filepath + '\\process\\' + filename + '\\%d.wav' % inx)
            audiofilepath = filepath + '\\process\\' + filename + '\\%d.wav' % inx
            text = sphinxapi(audiofilepath)
            text2 = text2srt(inx,text,start_t[inx],end_t[inx])
            f.writelines(text2)
        print(str(round((inx/len(pieces))*100))+'%')
    



def gotwave(audio, filename):
    new = pydub.AudioSegment.empty()
    for inx,val in enumerate(audio):
        new= val
        new.export(filepath + '\\process\\' + filename + '\\%d.wav' % inx,format='wav') 
    print('split done')

#二进制读取音频文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
    
def ms2s(ms):
    mspart=ms%1000
    mspart=str(mspart).zfill(3)
    spart=(ms//1000)%60
    spart=str(spart).zfill(2)
    mpart=(ms//1000)//60
    mpart=str(mpart).zfill(2)
    
    stype="00:"+mpart+":"+spart+","+mspart
    return stype



def text2srt(inx,text,starttime,endtime):
    strtext=str(inx)+'\n'+ms2s(starttime)+' --> '+ms2s(endtime)+'\n'+text+'\n'+'\n'
    return strtext



#filepath 是全局路径
#filename均为文件名不带路径带后缀

filepath = r'I:\音频\素材\pro studio'

if __name__ == '__main__':
    token = fetch_token()
    #video-api-text-srt
    batprocess(filepath)
    #srt-restruct for long srt
    batpro(filepath)