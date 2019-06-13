
from career import models
from bs4 import BeautifulSoup
import requests
import inspect
import sys
sys.path.append("/Users/sambong/libs/idebug")
sys.path.append("/Users/sambong/libs/ilib")
import idebug as dbg
import string
import re
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pprint
pp = pprint.PrettyPrinter(indent=2)


#============================================================
"""1차 Parser."""
#============================================================


#============================================================
"""2차 Parser."""
#============================================================

"""각 컬럼별 데이터변환"""

self = DataColumnsParser()
self.load_targets()
len(self.docs)
df = self.get_df()
df = self.clean_dtcols(df)
df.info()

numdf.info()


"""정수 + 문자열 혼합 변환"""

fraction_df = numdf.job_match_skills_ratio.str.extract(pat='(\d/\d+)([.\s]+)').reindex(columns=[0]).rename(columns={0:'fraction'})
fraction_df.sort_values('fraction').fraction.unique()
fraction_df['job_match_skills_ratio'] = fraction_df.fraction.apply(lambda x: x if x is np.nan else float( int(x.split('/')[0]) / int(x.split('/')[1]) ))
numdf.update(fraction_df)
numdf.join(fraction_df.reindex(columns=['fraction']))


job_applicants_df = numdf.job_applicants.str.extract(pat='(\d+)([.\s]+)').reindex(columns=[0]).rename(columns={0:'job_applicants'})
job_applicants_df.sort_values('job_applicants').job_applicants.unique()
job_applicants_df.job_applicants = job_applicants_df.job_applicants.apply(lambda x: x if x is np.nan else int(x) )
numdf.update(job_applicants_df)
# numdf.sort_values('job_applicants',ascending=False).head()




for col in sorted(self.num_cols):
    print(f"{'-'*60} col : {col}")
    print(f" unique_value_len : {numdf[col].nunique()}")
    print(f" type(value) : {type(numdf[col].to_list()[0])}")




df.posted_time_ago = df.posted_time_ago.apply(convert_to_ago_time)
df['posting_dt'] = df.collect_dt - df.posted_time_ago
df.reindex(columns=['posting_dt']+jp.schema).dropna(axis=1, how='all').sort_values('posted_time_ago')[:1]
def convert_to_skills_ratio(job_match_skills_ratio):
    if isinstance(job_match_skills_ratio, str):
        m = re.search('\d+/\d+',string=job_match_skills_ratio)
        if m is not None:
            nums = job_match_skills_ratio[m.start():m.end()].split('/')
            nums = [int(n) for n in nums]
            return round(nums[0]/nums[1], 1)

df.job_match_skills_ratio = df.job_match_skills_ratio.apply(convert_to_skills_ratio)
df.job_match_skills_ratio.mean()
df.job_match_skills_ratio.median()
