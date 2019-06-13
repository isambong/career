
import sys
import pandas as pd
import time
from datetime import datetime
sys.path.append('/Users/sambong/libs/ilib')
from ilib import inumber
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)


#============================================================
"""Tester."""
#============================================================

class FunctionIterator:

    def __init__(self, obj, func, dbgon=False, avg_runtime=1, **kwargs):
        self.obj = obj
        self.it = iter(obj)
        self.idx = 0
        self.len = len(obj)
        self.iterable = True
        self.func = func
        self.kwargs = kwargs
        self.start_dt = datetime.now().astimezone()
        self.dbgon = dbgon
        self.exp_runtime = avg_runtime

    def nextop(self):
        print(f"{'-'*60}\n pre-iterable : {self.iterable}")
        if self.iterable:
            try:
                print(f"next(self.it) : {next(self.it)}")
            except Exception as e:
                self.iterable = False
                print(f"{'*'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n StopIteration. self.iterable : {self.iterable}")
            else:
                self.func(next(self.it), **self.kwargs)
                self.iterable = True
                self.idx += 1
                self.report_loop()

    def report_loop(self):
        cum_runtime = (datetime.now().astimezone() - self.start_dt).total_seconds()
        avg_runtime = cum_runtime / (self.idx)
        leftover_runtime = avg_runtime * (self.len - self.idx)
        if self.dbgon:
            print(f"{'*'*60}\n{self.__class__} | {inspect.stack()[0][3]} : {self.idx}/{self.len}")
            print(f"Iterated function : {self.kwargs['caller']}")
            tpls = [
                ('누적실행시간', cum_runtime),
                ('잔여실행시간', leftover_runtime),
                ('평균실행시간', avg_runtime),
            ]
            for tpl in tpls:
                timeexp, unit = inumber.convert_timeunit(tpl[1])
                print(f" {tpl[0]} : {timeexp} ({unit})")
        if self.len == self.idx:
            if (self.exp_runtime is not None) and (avg_runtime > self.exp_runtime):
                print(f"{'*'*60}\n Save the final report into DB.")

# def func(it_value, **kwargs):
#     print(f"it_value : {it_value}")
#     print(f"kwargs :")
#     pp.pprint(kwargs)

def func(it_value, duration, sleepsecs):
    print(f"it_value : {it_value}")
    print(f"duration : {duration}")
    print(f"sleepsecs : {sleepsecs}")

func.__name__

search_keywords = [
    'data analytics',
    'data engineer',
    'machine learning',
    'python'
    'business intelligence (bi)',
    'data analysis',
    'Data Scientist',
    'Artificial Intelligence (AI)',
    'natural language processing',
    'Node.js']


# fi = FunctionIterator(search_keywords, func, dbgon=True, duration=10, sleepsecs=2)
# fi.it
# fi.idx
# fi.len
# fi.iterable
# fi.kwargs
# while fi.iterable:
#     fi.nextop()
