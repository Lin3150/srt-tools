#!/usr/bin/env python
# -*-coding:utf-8 -*-

import os

import glob




def transform(file):
    name = file.split('.')
    del name[len(name)-1]
    name = '.'.join(name)
    with open(file,'r') as f1:
        with open(name + ".srt",'w+') as f2:
            table = f1.read().split('\n')
            num = 0
            del table[0]
            for i in table:
                if i :
                    if '>' in i :
                        f2.write(format(i) + '\n')
                    else:
                        f2.write(i + '\n\n')
                else:
                    f2.write(str(num) + '\n')
                    num = num + 1
                
                    
def exec(absolutepath):
    for input_file in glob.glob(os.path.join(absolutepath, '*.vtt')):
        transform(input_file)    
        
def format(text):
    mm = text.split(' --> ')
    m1 = mm[0].split(':')
    m2 = mm[1].split(':')
    
    
    return '00:' + m1[0] + ':' + m1[1].replace('.', ',') + ' --> ' + '00:' + m2[0] + ':' + m2[1].replace('.', ',')


work_place = r'C:\Users\Administrator\Downloads\zimuchuli'
if __name__ == '__main__':
    exec(work_place)