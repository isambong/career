

import os
os.getcwd()
import sys
sys.path.append("/Users/sambong/pjts/career/env/lib/python3.7/site-packages")
sys.path.append("/Users/sambong/pjts/libs/idebug")
other_pjts = ['stock']
for other in other_pjts:
    path = f"/Users/sambong/pjts/{other}/env/lib/python3.7/site-packages"
    if path in sys.path:
        sys.path.remove(path)
sorted(sys.path)
import pprint
pp = pprint.PrettyPrinter(indent=2)

import requests



while True:
    r = requests.get('https://cargo.koreanair.com')
    print(r.status_code)
    if r.status_code is not 200:
        dbg.obj(r)
