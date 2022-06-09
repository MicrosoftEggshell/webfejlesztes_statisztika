# -*- coding: utf-8 -*-

from os import system

f = open('codes.txt', 'r')
codes = f.readlines()
codes = [s.strip() for s in filter(lambda x: x, codes)] # filter empty, strip linefeeds
f.close()

for i, code in enumerate(codes):
    if code:
        print('downloading ', i+1, '/', len(codes), ': ', code, sep='')
        system('wget -nv -o wget.log -m http://webfejlesztes.inf.elte.hu/2021222/honlapok/' + code)
        
system('move http://webfejlesztes.inf.elte.hu/2021222/honlapok .')