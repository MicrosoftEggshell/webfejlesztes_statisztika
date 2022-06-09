# -*- coding: utf-8 -*-

import requests
from html.parser import HTMLParser
import json

URL = 'http://webfejlesztes.inf.elte.hu/tarsertekeles/neptun.php'

class CodeParser(HTMLParser):

    in_td = False    
    codes = []

    def handle_starttag(self, startTag, attrs):
        if startTag == 'td':
            self.in_td = True
    
    def handle_endtag(self, endTag):
        if endTag == 'td':
            self.in_td = False

    def handle_data(self, data):
        if self.in_td and len(data) == 4:
            self.codes.append(data)


def scrape_codes(unscraped_codes):
    parser = CodeParser()
    unsuccessful_scrapes = []
    scraped_codes = {}
    
    while unscraped_codes:
    
        code = unscraped_codes.pop()
        try:
            r = requests.post(URL, data={'eha': code})
        except OSError: # csak ConnectionError lehet, de azt hiába próbáltam elkapni
            print('oopsie doopsie', code, 'unsuccessful')
            print('no worries i\'ll just try again')
            print('sit back and relax')
            # error handling + customer service 2in1
            unscraped_codes.add(code)
            continue
        parser.feed(r.text)
        if r.ok:
            scraped_codes[code] = parser.codes.copy()
            print(str(len(scraped_codes)) + ': ' + code, 'ok', parser.codes)
        else:
            print(code, 'failed')
            unsuccessful_scrapes.append(r.text)
    
        for c in parser.codes:
            if c not in scraped_codes:
                unscraped_codes.add(c)
                
        parser.codes.clear()
    
    if 'r' in locals():
        r.close()
    
    return scraped_codes

def reverse_dict(dic):
    ret = {}
    
    for k, l in dic.items():
        for v in l:
            if v not in ret:
                ret[v] = []
            ret[v].append(k)
    
    return ret

if __name__ == '__main__':
    scraped_codes = {}
    try:
        f = open('forward_codes.json', 'r')
        scraped_codes = json.loads(f.read())
    except (IOError, json.JSONDecodeError):
        scraped_codes = scrape_codes({'fp2t'})
    finally:
        if 'f' in locals():
            f.close()
    
    f = open('forward_codes.json', 'w')
    f.write(json.dumps(scraped_codes))
    f.close()

    f = open('backward_codes.json', 'w')
    f.write(json.dumps(reverse_dict(scraped_codes)))
    f.close()
    
    f = open('codes.txt', 'w')
    for k in scraped_codes:
        f.write(k)
        f.write ('\n')
    f.close()
    
