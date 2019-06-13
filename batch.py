
import schedule
import time
from datetime import datetime, date, tzinfo, timedelta, timezone
from career import linkedin
import sys
import inspect
import idebug as dbg
from selenium import webdriver


driver = webdriver.Chrome()


def cron_linkedin_jobs():
    fr = dbg.Function(inspect.currentframe()).report_init()
    ############################################################
    search_keywords = [
        'Data Analytics',
        'Data Analysis',
        'Data Scientist',
        'Data Science',
        'Data Engineer',
        'Machine Learning',
        'Artificial Intelligence (AI)',
        'Natural Language Processing',
        'Business Intelligence (bi)',
        'Python',
        'Node.js',
    ]
    lid = linkedin.LinkedInDriver(driver)
    lid.login().setup_services()
    lid.jobs.collect_on_keywords(location='Spain', duration=0)
    lid.jobs.collect_on_keywords(location='United Kingdom', duration=0)
    ############################################################
    dup = linkedin.jobs.Deduplicator()
    dup.load_targets().delete_dup_data()
    ############################################################
    linkedin.jobs.parse()
    ############################################################
    fr.report_fin()

def jobs():
    print(f"\n {inspect.stack()[0][3]} :\n{inspect.getdoc(jobs)}\n")
    ############################################################
    schedule.every().days.at("09:00").do(cron_linkedin_jobs).run()
    ############################################################
    while True:
        schedule.run_pending()
        time.sleep(0.01)


if __name__ == '__main__':
    print(f"{'='*60}\n sys.modules[__name__].__file__ : {sys.modules[__name__].__file__}")
    jobs()
