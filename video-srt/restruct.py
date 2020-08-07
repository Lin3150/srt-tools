#!/usr/bin/env python
# -*-coding:utf-8 -*-

import os
import glob
import nltk



#找到其中的srt文件并逐个处理
def batpro(path):
    for input_file in glob.glob(os.path.join(path, '*.srt')):
        singlepro(input_file)

#单个文件处理
def singlepro(file):
    with open(file, 'r') as readfile:
        content = readfile.read()
    with open(file, 'w') as writefile:
        content = content.split('\n\n')
        addpattern = 0
        for i in content:
            pattern = i.split('\n')
            if len(pattern) > 1:         
                if len(pattern[2]) > 150:
                    timepart = pattern[1]
                    num = int(pattern[0]) + addpattern
                    time1, time2 = timepart.split(' --> ')
                    s_time = srttime2ms(time1)
                    e_time = srttime2ms(time2)
                    s_timelist, e_timelist, wordlist = srt(s_time, e_time, pattern[2])
                    for i in range(len(wordlist)):
                        num = num + i
                        s_time = ms2srttime(s_timelist[i])
                        e_time = ms2srttime(e_timelist[i])
                        #writelines不会自动换行，需要手动加'\n'
                        writefile.writelines(str(num) + '\n' + s_time + ' --> ' + e_time + '\n' + nolmal(wordlist[i]) + '\n\n')               
                    addpattern = addpattern + len(wordlist) - 1
                else:
                    num = int(pattern[0]) + addpattern
                    timepart = pattern[1]
                    writefile.writelines(str(num) + '\n' + str(timepart) + '\n' + pattern[2] + '\n\n')

def nolmal(sent):
    sent = sent.replace(' \'', '\'')
    return sent

def srttime2ms(srttime):
    hpart, mpart, sandmspart = srttime.split(':')
    spart, mspart = sandmspart.split(',')
    ms = int(hpart) * 60 * 60 * 1000 + int(mpart) * 60 * 1000 + int(spart) * 1000 + int(mspart)
    return ms

def ms2srttime(ms):
    mspart = ms % 1000
    mspart = str(mspart).zfill(3)
    spart = (ms // 1000) % 60
    spart = str(spart).zfill(2)
    mpart = (ms // 1000) // 60
    mpart = str(mpart).zfill(2)
    hpart = (ms // 1000) // 60 // 60
    hpart = str(hpart).zfill(2)
    stype = hpart + ':' + mpart + ":" + spart + "," + mspart
    return stype

def sentsplit(sent):
    alist = []
    worddic = nltk.word_tokenize(sent)
    process = nltk.pos_tag(worddic)
    typeone = 0
    if nltk.pos_tag([worddic[0]])[0][1] == 'CC':
        alist.append(worddic[0])
        worddic = worddic[1:]
        process = nltk.pos_tag(worddic)
        typeone = 1
    for word,tag in process:
        if tag == 'CC':
            break
        alist.append(word)
    if typeone == 1:
        blist = worddic[len(alist) - 1:] 
    else:
        blist = worddic[len(alist):]   
    if len(alist) + 1 >= len(worddic):
        alist = []
        worddic = nltk.word_tokenize(sent)
        process = nltk.pos_tag(worddic)
        typeone = 0
        if nltk.pos_tag([worddic[0]])[0][1] == 'IN':
            alist.append(worddic[0])
            worddic = worddic[1:]
            process = nltk.pos_tag(worddic)
            typeone = 1
        for word,tag in process:
            if tag == 'IN':
                break
            alist.append(word)
        if typeone == 1:
            blist = worddic[len(alist) - 1:] 
        else:
            blist = worddic[len(alist):]         
    a = ' '.join(alist)
    b = ' '.join(blist)
    return a,b

def itrepro(sent, thershold = 150):
    res = []
    a, b = sentsplit(sent)

    if len(a) > thershold:
        a1, a2 = sentsplit(a)
        if len(a1) > thershold:
            a11, a12 = sentsplit(a1)
            res.append(a11)
            res.append(a12)
        else:
            res.append(a1)
        if len(a2) > thershold:
            a21, a22 = sentsplit(a2)
            res.append(a21)
            res.append(a22)
        else:
            res.append(a2)
    else:
        res.append(a)
    if len(b) > thershold:
        b1, b2 = sentsplit(b)
        if len(b1) > thershold:
            b11, b12 = sentsplit(b1)
            res.append(b11)
            res.append(b12)
        else:
            res.append(b1)
        if len(b2) > thershold:
            b21, b22 = sentsplit(b2)
            res.append(b21)
            res.append(b22)
        else:
            res.append(b2)        
    else:
        res.append(b)
    return res

def srt(s_time, e_time, word):
    a = itrepro(word)
    slice_num = len(a)
    all_time = int(e_time) - int(s_time)
    all_length = 0
    for i in a:
        all_length = all_length + len(str(i))
    timeslice = []
    for i in a:
        timeslice.append(int(len(str(i)) / all_length * all_time))
    s_time_list = []
    e_time_list = []
    s_time_list.append(s_time)
    temp = int(s_time)
    for i in range(len(a)-1) :
        temp = temp + timeslice[i]
        s_time_list.append(temp)
        e_time_list.append(temp)
    e_time_list.append(e_time)
    return s_time_list, e_time_list, a



#确定工作区域
path = r'I:\音频\素材\ACOUSTIC POP MIX DECONSTRUCTION'
if __name__ == '__main__':
    batpro(path)