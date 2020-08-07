#!/usr/bin/env python
# -*-coding:utf-8 -*-


import http.client
import hashlib
import urllib
import random
import json
import re
import os
import glob
import time
import requests
from tqdm import tqdm


#baidu-api part
appid = '20180301000129384' 
secretKey = 'lleLzYw1DoRz1_9CYML6' 


def translate(word):
    myurl = '/api/trans/vip/translate'
    q = word
    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    oddsign = appid+q+str(salt)+secretKey
    m1 = hashlib.md5()
    sign = oddsign.encode(encoding='utf-8')
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        temp = response.read().decode()
        tempp = json.loads(temp)

        return tempp['trans_result'][0]['dst']
    except Exception as e:
        return e
    finally:
        if httpClient:
            httpClient.close()

#limit time for api
#prevent from i/o block
def limittranslate(word):
    global oritime 
    oritime = time.perf_counter()
    global nowtime 
    nowtime = time.perf_counter()   
    while nowtime - oritime < 10:
        if nowtime - oritime > 1:
            oritime = nowtime
            nowtime = time.perf_counter()
            return translate(word)
            break
        else:
            nowtime = time.perf_counter()


#translate for one file   
def solve(file):
    name = file.split('.')
    fo = open(file, 'r', encoding='utf-8')
    ff = open(name[0]+'translated'+'.srt','w', encoding='utf-8')
    table = fo.read().split('\n')
    fo.seek(0, 0)
    ff.seek(0, 0)
    for linenum in tqdm(range(len(table))):
        if (linenum - 2) % 4 == 0:
            ff.write(limittranslate(fo.readline().strip('\n'))+'\n')
        else:
            ff.write(fo.readline())
    ff.close()
    fo.close()
    print('work done')


#bat translate
def trans(path):
    for input_file in glob.glob(os.path.join(path, '*.srt')):
        solve(input_file)

def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()



#sougou-api part
pid = "297076a6cb3fe40973573a07703adb37"     
key = "6f3cecaced4518b872fcc6ea8010e0e9"  
def sogoutranlator(text):
    url = "http://fanyi.sogou.com:80/reventondc/api/sogouTranslate"      
    salt = "1508404016012"      #随机数，可以填入时间戳
    q = text    
    sign = md5(pid+q+salt+key)
    fro = "en"     
    to = "zh-CHS"   
    payload = "from=" + fro + "&to=" + to + "&pid=" + pid + "&q=" + urllib.parse.quote(q) + "&sign=" + sign + "&salt=" + salt
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return json.loads(response.text)['translation']   

#limit time for api
#prevent from i/o block
def limitsogoutranslate(word):
    time.sleep(0.5)   
    return sogoutranlator(word)

#solve onefile
def sogousolve(file):
    name = file.split('.')
    fo = open(file, 'r', encoding='utf-8')
    ff = open(name[0]+'translated'+'.srt','w', encoding='utf-8')
    table = fo.read().split('\n')
    fo.seek(0, 0)
    ff.seek(0, 0)
    for linenum in tqdm(range(len(table))):
        if (linenum - 2) % 4 == 0:
            ff.write(limitsogoutranslate(fo.readline().strip('\n'))+'\n')
        else:
            ff.write(fo.readline())
    ff.close()
    fo.close()
    print('work done')

#bat translate
def sogoutrans(path):
    for input_file in glob.glob(os.path.join(path, '*.srt')):
        sogousolve(input_file)
        
#second way to process the srt subtitle
#for debug
def doublesogousolve(file):
    name = file.split('.')
    fo = open(file, 'r', encoding='utf-8')
    ff = open(name[0]+'translated'+'.srt','w', encoding='utf-8')
    table = fo.read().split('\n')
    fo.seek(0, 0)
    ff.seek(0, 0)
    for linenum in tqdm(range(len(table))):
        if (linenum - 2) % 5 == 0:
            fo.readline()
        elif (linenum - 3) % 5 == 0:
            engline = fo.readline().strip('\n')
            ff.write(limitsogoutranslate(engline) + '\n')
        elif (linenum - 4) % 5 == 0:
            fo.readline()
            ff.write(engline + '\n' + '\n')
        else:
            ff.write(fo.readline())
    ff.close()
    fo.close()
    print('work done')    

def doublesogoutrans(path):
    for input_file in glob.glob(os.path.join(path, '*.srt')):
        doublesogousolve(input_file)


#you should config your api key for yourself
input_path = 'E:\\字幕处理项目'
if __name__ == '__main__':
    trans(input_path)



