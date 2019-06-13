
"""
Version : 1
"""

# import sys
# sys.path.append("/Users/sambong/pjts/career/env/lib/python3.7/site-packages")
# sys.path.append('/Users/sambong/libs/idebug')
# sys.path.append('/Users/sambong/libs/ilib')
# other_pjts = ['stock']
# for other in other_pjts:
#     path = f"/Users/sambong/pjts/{other}/env/lib/python3.7/site-packages"
#     if path in sys.path:
#         sys.path.remove(path)
# sorted(sys.path)
# %env USERID=iinnovata@gmail.com
# %env PW=5272Dkgkgk
# # export USERID=iinnovata@gmail.com
# # export PW=5272Dkgkgk
# import pprint
# pp = pprint.PrettyPrinter(indent=2)


import sys
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from career import models
from career.iiterator import FunctionIterator
import string
from collections import Counter
import inspect
from pandas.io.json import json_normalize
# from career.linkedin.general import LinkedInDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, urlencode, parse_qs
import time
import json
from datetime import datetime
sys.path.append('/Users/sambong/libs/idebug')
sys.path.append('/Users/sambong/libs/ilib')
import idebug as dbg
from ilib import inumber
import copy

#============================================================
"""Log-in by selenium."""
"""driver는 전역변수-객체로써 사용된다."""
#============================================================



class SearchConditionSetter:
    """검색조건 설정."""
    base_url = 'https://www.linkedin.com/jobs/search/'

    def __init__(self, driver):
        self.driver = driver
        self.move_to_job_search_page()

    def move_to_job_search_page(self):
        if re.search(self.base_url, string=self.driver.current_url) is None:
            print("\n 현재페이지가 Job Search page가 아니므로, 검색페이지로 이동.\n")
            self.driver.get(self.base_url)
        else:
            pass

    def put_searching_keyword(self, keyword='Data Analytics', location='Spain'):
        # 나중 분석을 위한 참고사항.
        #nav = self.driver.find_element_by_id('extended-nav')
        #search_form = nav.find_element_by_id('extended-nav-search')
        try:
            search_form = self.driver.find_element_by_id('nav-typeahead-wormhole')
        except Exception as e:
            print(f"{'#'*60}\n{inspect.stack()[0][3]}\n e : {e}")
            self.put_searching_keyword(keyword, location)
        else:
            keyword_box = search_form.find_element_by_xpath("//div[contains(@class, 'jobs-search-box__input--keyword')]")
            location_box = search_form.find_element_by_xpath("//div[contains(@class, 'jobs-search-box__input--location')]")
            search_button = search_form.find_element_by_xpath("//button[contains(@class, 'jobs-search-box__submit-button')]")

            keyword_box = keyword_box.find_element_by_tag_name('artdeco-typeahead-deprecated').find_elements_by_tag_name('input')[1]
            keyword_box.clear()
            print(" 검색 키워드 입력시간 3초 설정.")
            time.sleep(3)
            keyword_box.send_keys(keyword)

            location_box = location_box.find_element_by_tag_name('artdeco-typeahead-deprecated').find_elements_by_tag_name('input')[1]
            location_box.clear()
            print(" 지역명 입력시간 3초 설정.")
            time.sleep(3)
            location_box.send_keys(location)

            print(" 검색 버튼 누르는 시간 1초 설정.")
            time.sleep(1)
            search_button.click()
            return self

    def choose_posted_duration(self, duration=0):
        """
        past24hours = duration : [0]
        past_week = duration : [1]
        past_month = duration : [2]
        anytime = duration : [3]
        """
        time.sleep(2)
        try:
            filterbar_section = self.driver.find_element_by_xpath('//header[contains(@class, "search-filters-bar--jobs-search")]')
        except Exception as e:
            print(f"{'#'*60}\n{inspect.stack()[0][3]}\n e : {e}")
            self.choose_posted_duration(duration)
        else:
            date_filter = filterbar_section.find_element_by_xpath("//button[contains(@aria-label, 'Date Posted filter')]")
            # 드롭-다운 선택지 불러오기.
            time.sleep(1)
            date_filter.find_element_by_tag_name('li-icon').click()
            facets = filterbar_section.find_element_by_id("date-posted-facet-values")
            values = facets.find_elements_by_tag_name('li')
            # 기간 선택.
            time.sleep(1)
            values[duration].find_element_by_tag_name('label').click()
            # 필터 적용.
            time.sleep(1)
            facets.find_element_by_xpath("//button[contains(@data-control-name, 'filter_pill_apply')]").click()
            time.sleep(1)
            return self

    def set_sorting(self, sort='date'):
        try:
            sort_section = self.driver.find_element_by_id('sort-by-select')
        except Exception as e:
            print(f"{'#'*60}\n{inspect.stack()[0][3]}\n e : {e}")
            self.set_sorting(sort)
        else:
            sort_button = sort_section.find_element_by_id("sort-by-select-trigger")
            sort_option = sort_section.find_element_by_id('sort-by-select-options')
            cur_sort_value = sort_button.find_element_by_tag_name('p').text
            if sort not in cur_sort_value:
                # 옵션 선택 팝업 클릭.
                time.sleep(1)
                sort_button.find_element_by_tag_name('p').click()
                class_pat = f"jobs-search-dropdown__option-button--{sort}"
                xpath = f"//button[contains(@class, '{class_pat}')]"
                # 최종 옵션 선택 및 적용.
                time.sleep(1)
                sort_option.find_element_by_xpath(xpath).click()
            return self

    def setup_default_search_condition(self):
        uo = urlparse(self.driver.current_url)
        if ('keywords' in uo.query) and ('location' in uo.query):
            pass
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n keywords와 locations이 url에 없다.\n driver.current_url : {self.driver.current_url}")
            self.put_searching_keyword('data analytics', 'spain').choose_posted_duration(0).set_sorting('date')
        return self


#============================================================
"""Collector"""
#============================================================


class Collector(models.LinkedInJobPosting):

    def __init__(self, driver, nextpage_click_secs=3, jobcard_click_secs=2, job_details_human_reading_secs=30):
        super().__init__()
        self.driver = driver
        # self.move_to_job_search_page()
        # self.extract_keyword_location()
        self.collect_dt = datetime.now().astimezone()
        self.job_details_human_reading_secs = job_details_human_reading_secs
        self.jobcard_click_secs = jobcard_click_secs
        self.nextpage_click_secs = nextpage_click_secs

    def is_readyto_collect(self):
        uo = urlparse(self.driver.current_url)
        if ('keywords' in uo.query) and ('location' in uo.query) and ('sortBy' in uo.query):
            return True
        else:
            return False

    def extract_keyword_location(self):
        uo = urlparse(self.driver.current_url)
        qs = parse_qs(uo.query)
        self.search_keyword = qs['keywords'][0]
        self.search_location = qs['location'][0]

    def detect_jobcards(self):
        jobcards_container = self.driver.find_elements_by_class_name('jobs-search-two-pane__results')
        if len(jobcards_container) is 1:
            jobcards_contents = self.driver.find_elements_by_class_name('jobs-search-results')
            if len(jobcards_contents) is 1:
                jobcard_ul = self.driver.find_elements_by_class_name('jobs-search-results__list')
                if len(jobcard_ul) is 1:
                    jobcards = self.driver.find_elements_by_class_name('artdeco-list__item')
                    self.jobcards = FunctionIterator(jobcards, self._click)
                    print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Job-cards exist.")
                else:
                    print(f"\n len(jobcard_ul) is not 1.\n")
            else:
                print(f"\n len(jobcards_contents) is not 1.\n")
        else:
            print(f"\n len(jobcards_container) is not 1.\n")
        return self

    def parse_jobcard(self):
        active_jobcard = self.driver.find_elements_by_class_name('job-card-search--is-active')
        if len(active_jobcard) is 1:
            jobcard = active_jobcard[0].find_elements_by_class_name('job-card-search__content-wrapper')
            if len(jobcard) is 1:
                job_title = jobcard[0].find_elements_by_class_name('job-card-search__title')
                if len(job_title) is 1:
                    self.title = job_title[0].text
                else:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(job_title) is not 1.\n")

                companyname = jobcard[0].find_elements_by_class_name('job-card-search__company-name')
                if len(companyname) is 1:
                    self.companyname = companyname[0].text
                else:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(companyname) is not 1.\n")

                location = jobcard[0].find_elements_by_class_name('job-card-search__location')
                if len(location) is 1:
                    self.location = location[0].text
                else:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(location) is not 1.\n")

            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(jobcard) is not 1.\n")
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 이런 경우는 절대 발생할 수 없다.\n")

    def _click(self, webelem):
        """job-card-search--is-active"""
        try:
            webelem.click()
        except Exception as e:
            pass

    def detect_job_details(self):
        rightpanel_container = self.driver.find_elements_by_class_name('jobs-search-two-pane__details')
        if len(rightpanel_container) is 1:
            content_container = self.driver.find_elements_by_class_name('jobs-details__main-content')
            if len(content_container) is 1:
                print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Right-panel exists.\n")
                return True
            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(content_container) is not 1.\n")
                return False
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(rightpanel_container) is not 1.\n")
            return False

    def debug_re_search(self, sleepsecs=3):
        time.sleep(sleepsecs)
        print(f"{'*'*60}\n{self.__class__} | {inspect.stack()[0][3]}")
        html = self.driver.page_source

        m = re.search('jobs-premium-applicant-insights\s*',string=html)
        print(f"{'-'*60}\n jobs-premium-applicant-insights\s* re.search :\n {m}")

        m = re.search('jobs-premium-company-insights\s*',string=html)
        print(f"{'-'*60}\n jobs-premium-company-insights\s* re.search :\n {m}")

        m = re.search('jobs-company__card\s*',string=html)
        print(f"{'-'*60}\n jobs-company__card\s* re.search :\n {m}")

    def click_job_description_see_more(self, sleepsecs=5):
        """See More"""
        time.sleep(sleepsecs)
        job_description = self.driver.find_elements_by_class_name('jobs-description')
        see_more_btn = job_description[0].find_elements_by_class_name('artdeco-button')
        try:
            see_more_btn[0].click()
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 무시하라.")
            pass

    def click_applicant_insights_send_feedback(self, sleepsecs=2):
        """Send Feedback"""
        time.sleep(sleepsecs)
        applicant_insights = self.driver.find_elements_by_class_name('jobs-premium-applicant-insights')
        if len(applicant_insights) is 1:
            send_feedback = applicant_insights[0].find_elements_by_class_name('display-flex')
            if len(send_feedback) is 1:
                ActionChains(driver).move_to_element(send_feedback[0]).perform()
            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(send_feedback) is not 1.")
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(applicant_insights) is not 1.")

    def click_company_insights_more_company(self, sleepsecs=2):
        """See more company insights"""
        time.sleep(sleepsecs)
        company_insights = self.driver.find_elements_by_class_name('jobs-premium-company-insights')
        if len(company_insights) is 1:
            try:
                more_company = company_insights[0].find_element_by_xpath("//a[contains(@data-control-name, 'see_more_company_link')]")
            except Exception as e:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 무시하라.")
                pass
            else:
                ActionChains(driver).move_to_element(more_company).perform()
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(company_insights) is not 1.")

    def save_job_details(self):
        if hasattr(self,'search_keyword') and hasattr(self,'search_location') and hasattr(self,'companyname') and hasattr(self,'title'):
            self.html = self.driver.page_source
            filter = {
                'search_keyword':self.search_keyword,
                'search_location':self.search_location,
                'collect_dt':self.collect_dt,
                'companyname':self.companyname,
                'title':self.title,
            }
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n list(self.schematize().doc) : {list(self.schematize().doc)}.")
            self.insert_doc()
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 중요한 키값을 가지고 있지 않기 때문에 저장하지 않는다.\n")
        return self
    """삭제 대상"""
    def detect_pagination(self):
        pagination_indicator = self.driver.find_elements_by_class_name('artdeco-pagination__indicator--number')
        if len(pagination_indicator) is 0:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(pagination_indicator) is 0.\n")
            return False
        else:
            self.pagination_indicators = []
            for indicator in pagination_indicator:
                self.pagination_indicators.append(indicator)
            # self.pagination = FunctionIterator(self.pagination_indicators, self.paginate)
            return True

    def selected_page(self, addi_info=None):
        pagination_pages = self.driver.find_elements_by_class_name('artdeco-pagination__pages--number')
        if len(pagination_pages) is 1:
            selected = pagination_pages[0].find_elements_by_class_name('selected')
            if len(selected) is 1:
                self._selected_page = selected[0].text
                print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]} : {self._selected_page} ({addi_info})")
            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(selected) is not 1.\n")
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(pagination_pages) is not 1.\n")
        return self
    """삭제 대상"""
    def paginate(self):
        """return next_clickable : True | False"""
        if self.detect_pagination():
            self.selected_page("current_page_num")
            if hasattr(self, 'pagination_indicators'):
                page_click_on = False
                for indicator in self.pagination_indicators:
                    if page_click_on is True:
                        indicator.click()
                        self.selected_page("moved_page_num")
                        return True
                    else:
                        pass

                    if self._selected_page == indicator.find_element_by_tag_name('span').text:
                        page_click_on = True
                    else:
                        pass
                return False
            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n hasattr(self, 'pagination_indicators') is False.\n")
                return False
        else:
            return False
    """삭제 대상"""
    def paginate_v1(self, cur_pagenum, last_pagenum, sleepsecs):
        while cur_pagenum <= last_pagenum:
            time.sleep(sleepsecs)
            pagination = self.driver.find_element_by_tag_name('artdeco-pagination')
            cur_pbutton = pagination.find_element_by_xpath('//li[contains(@class, "active selected")]')
            cur_pagenum = int(cur_pbutton.find_element_by_tag_name('span').text)
            print(f"{'-'*60}\n page-number progress : {cur_pagenum}/{last_pagenum}")
            ############################################################

            collect_1page()

            ############################################################
            """다음 페이지 번호를 찾아서 클릭."""
            page_buttons = pagination.find_elements_by_tag_name('li')
            cur_i = None
            for i, pbutton in enumerate(page_buttons, start=1):
                if pbutton.find_element_by_tag_name('span').text == str(cur_pagenum):
                    cur_i = i
                if (cur_i is not None) and (i is cur_i+1):
                    print(f" Go to next page.")
                    pbutton.click()
                    break
            if cur_pagenum is last_pagenum:
                print(f" This is the last page. Stop.")
                cur_pagenum += 1
                break
            fr.report_mid(addi_info=f" cur_pagenum : {cur_pagenum} 완료.")
        fr.report_fin()

    def collect_job_details(self):
        if self.detect_job_details():
            self.click_job_description_see_more(5)
            self.click_applicant_insights_send_feedback(2)
            self.click_company_insights_more_company(2)
            self.debug_re_search(3)
            """sleepsecs 동안 job-details 읽는 척."""
            time.sleep(self.job_details_human_reading_secs)
            self.save_job_details()
        else:
            pass

    def loop_jobcards(self):
        self.detect_jobcards()
        while self.jobcards.iterable:
            """2초 후에 다음 job-card를 클릭."""
            time.sleep(self.jobcard_click_secs)
            self.jobcards.nextop()
            self.parse_jobcard()
            self.collect_job_details()
            # break
    """삭제 대상"""
    def loop_pagination_v1(self, sleepsecs=3):
        pg_result = True
        while pg_result:
            self.loop_jobcards()
            """다음 페이지 버튼을 누르기까지 sleepsecs 만큼 걸린다."""
            time.sleep(sleepsecs)
            pg_result = self.paginate()
            # break

    def loop_pagination(self):
        pi = PaginationIterator(func=self.loop_jobcards)
        while pi.iterable:
            pi.nextop()
            """다음 페이지 버튼을 누르기까지 sleepsecs 만큼 걸린다."""
            time.sleep(self.nextpage_click_secs)
            # break

class PaginationIterator:
    """동적으로 페이지 리스트가 변할 때 사용."""
    def __init__(self, func, dbgon=False, avg_runtime=1):
        self.start_dt = datetime.now().astimezone()
        self.dbgon = dbgon
        self.exp_runtime = avg_runtime
        self.func = func
        """Pagination 이 존재하든 말든 초기 1회 무조건 실행."""
        self.setup_pagination()
        self.func()
        self.report_loop()

    def setup_pagination(self):
        pagination_pages = self.driver.find_elements_by_class_name('artdeco-pagination__pages--number')
        if len(pagination_pages) is 1:
            indicators = pagination_pages[0].find_elements_by_class_name('artdeco-pagination__indicator--number')
            if len(indicators) is 0:
                self.iterable = False
                self.page = 1
                self.len = 1
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(indicators) is 0.\n")
            else:
                self.iterable = True
                self.indicators = indicators
                self.idx = 0
                self.page = 1
                self.len = int(indicators[-1].text.strip())
        else:
            self.iterable = False
            self.page = 1
            self.len = 1
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(pagination_pages) is not 1.\n")
        return self

    def nextop(self):
        try:
            self.indicators[self.idx +1].click()
        except Exception as e:
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Stop Iteration.")
            self.iterable = False
        else:
            self.func()
            self.page += 1
            self.report_loop()
            self.renew_curpage()

    def renew_curpage(self):
        pagination_pages = self.driver.find_elements_by_class_name('artdeco-pagination__pages--number')
        if len(pagination_pages) is 1:
            indicators = pagination_pages[0].find_elements_by_class_name('artdeco-pagination__indicator--number')
            if len(indicators) is 0:
                self.iterable = False
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(indicators) is 0.\n")
            else:
                self.iterable = True
                self.indicators = indicators
                for i, indicator in enumerate(indicators):
                    m = re.search('selected', string=indicator.get_attribute('class'))
                    if m is None:
                        pass
                    else:
                        self.idx = i
                        self.page = int(indicator.text.strip())
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(pagination_pages) is not 1.\n")
        return self

    def report_loop(self):
        cum_runtime = (datetime.now().astimezone() - self.start_dt).total_seconds()
        avg_runtime = cum_runtime / (self.page)
        leftover_runtime = avg_runtime * (self.len - self.page)
        if self.dbgon is True:
            print(f"{'*'*60}\n{self.__class__} | {inspect.stack()[0][3]} : {self.page}/{self.len}")
            tpls = [
                ('누적실행시간', cum_runtime),
                ('잔여실행시간', leftover_runtime),
                ('평균실행시간', avg_runtime),
            ]
            for tpl in tpls:
                timeexp, unit = inumber.convert_timeunit(tpl[1])
                print(f" {tpl[0]} : {timeexp} ({unit})")
        if self.len == self.page:
            if (self.exp_runtime is not None) and (avg_runtime > self.exp_runtime):
                print(f"{'*'*60}\n Save the final report into DB.")

class JobsCollector(SearchConditionSetter, Collector):

    search_keywords = [
        'data analytics',
        'data analysis',
        'Data Scientist',
        'Data Science',
        'data engineer',
        'machine learning',
        'Artificial Intelligence (AI)',
        'natural language processing',
        'business intelligence (bi)',
        'python',
        'Node.js',
    ]

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def collect_on_keyword(keyword='machine learning', location='Spain', duration=0, pagination_sleep=3):
        fr = dbg.Function(inspect.currentframe()).report_init()
        nextpage_click_secs = pagination_sleep
        jobcard_click_secs = 3
        job_details_human_reading_secs = 20
        c = Collector(nextpage_click_secs, jobcard_click_secs, job_details_human_reading_secs)
        c.move_to_job_search_page()
        c.put_searching_keyword(keyword, location).choose_posted_duration(duration).set_sorting('date')
        c.extract_keyword_location()
        c.loop_pagination()
        fr.report_fin()

    def collect_on_keywords(search_keywords):
        fi = FunctionIterator(search_keywords, collect_on_keyword)
        while fi.iterable:
            fi.nextop()


#============================================================
"""Tester."""
#============================================================
