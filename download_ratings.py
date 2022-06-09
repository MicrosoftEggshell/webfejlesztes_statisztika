# -*- coding: utf-8 -*-

import requests

URL = 'http://webfejlesztes.inf.elte.hu/eredmeny/ertekelesek.php'

import json
import os

f = open('backward_codes.json', 'r')
codes = json.loads(f.read())

folder = 'ertekelesek'

# lopva https://www.tutorialspoint.com/How-can-I-create-a-directory-if-it-does-not-exist-using-Python
if not os.path.exists(folder):
    os.makedirs(folder)

for i, code in enumerate(codes, 1):
    print(i, '/', len(codes), ': ', code, sep='')
    try:
        f = open(folder + '/' + code + '.html', 'x', encoding='utf-8')
    except IOError:
        i += 1
        continue # file is already downloaded
    try:
        r = requests.post(URL, data={'eha': code})
        i += 1
    except OSError: # csak ConnectionError lehet, de azt hiába próbáltam elkapni
        print('oopsie doopsie', code, 'unsuccessful')
    r.encoding = 'utf-8'
    f.write(r.text \
            .replace('</h2>', '</h2><h3>Társértékelők: <a href="' + codes[code][0] + '.html">' + codes[code][0] + '</a>, ' \
                     '<a href="' + codes[code][1] + '.html">' + codes[code][1] + '</a></h3>') \
            .replace('honlapjának', '<a href="http://webfejlesztes.inf.elte.hu/2021222/honlapok/' + code + '" target="_blank">' + 'honlapjának</a>') \
            )
    f.close()

if 'r' in locals():
    r.close()