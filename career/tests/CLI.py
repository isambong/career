
#============================================================
# 환경변수 셋업.
#============================================================

export DART_API_AUTH_KEY=7652d9f6e7f3c3071d2ad5c6a49191a8d03cb5c8

#============================================================
# excutions.
#============================================================
from career.batch import *

#============================================================
# tests.
#============================================================
from career.tests import iiterator
iiterator.tests()


import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
import os
import sys

sys.meta_path
sys.path[0].replace('/stock', '')
m = sys.modules
pp.pprint(list(m.keys()))
m[__name__]
for k, v in m.items():
    #if isinstance(v, object):
    print(f"\n key : {k}\n val : {v}")
