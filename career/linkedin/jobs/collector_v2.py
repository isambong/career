
"""
Version : 2
2019-05-29 기준,
LinkedIn 에서 25개 이상의 JobCards를 페이지 네비게이션 방식에서 Ajax기반의 스크롤 방식으로 변경했다.
따라서 version2에서 사용했던 Pagination 은 필요없고 version3에서는 Scroller를 새로 개발해야한다.
"""


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
"""Clicker."""
#============================================================

class SearchConditionSetter:
    """검색조건 설정."""
    base_url = 'https://www.linkedin.com/jobs/search/'

    def __init__(self, keywords_writing_secs=3, searchbutton_click_secs=1):
        super(SearchConditionSetter, self).__init__()
        self.keywords_writing_secs = keywords_writing_secs
        self.searchbutton_click_secs = searchbutton_click_secs
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
            print(f" 검색 키워드 입력시간 {self.keywords_writing_secs}초 설정.")
            time.sleep(self.keywords_writing_secs)
            keyword_box.send_keys(keyword)

            location_box = location_box.find_element_by_tag_name('artdeco-typeahead-deprecated').find_elements_by_tag_name('input')[1]
            location_box.clear()
            print(f" 지역명 입력시간 {self.keywords_writing_secs}초 설정.")
            time.sleep(self.keywords_writing_secs)
            location_box.send_keys(location)

            print(f" 검색 버튼 누르는 시간 {self.searchbutton_click_secs}초 설정.")
            time.sleep(self.searchbutton_click_secs)
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

class JobDetails(models.LinkedInJobPosting):

    def __init__(self):
        super().__init__()

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

    def collect_job_details(self):
        if self.detect_job_details():
            self.click_job_description_see_more(5)
            self.click_applicant_insights_send_feedback(2)
            self.click_company_insights_more_company(2)
            self.debug_re_search(3)
            print(f"{'*'*60}\n.\n.\n.\n {self.job_details_human_reading_secs}초 동안 job-details 읽는 척.\n.\n.\n.")
            time.sleep(self.job_details_human_reading_secs)
            self.save_job_details()
        else:
            pass

class JobCards:

    def __init__(self):
        super(JobCards, self).__init__()

    def _click(self, webelem, **kwargs):
        """job-card-search--is-active"""
        try:
            webelem.click()
        except Exception as e:
            pass

    def detect_jobcards(self):
        jobcards_container = self.driver.find_elements_by_class_name('jobs-search-two-pane__results')
        if len(jobcards_container) is 1:
            jobcards_contents = self.driver.find_elements_by_class_name('jobs-search-results')
            if len(jobcards_contents) is 1:
                jobcard_ul = self.driver.find_elements_by_class_name('jobs-search-results__list')
                if len(jobcard_ul) is 1:
                    jobcards = self.driver.find_elements_by_class_name('artdeco-list__item')
                    self.jobcards_it = FunctionIterator(obj=jobcards, func=self._click, dbgon=True, caller=f"{self.__class__} | {inspect.stack()[0][3]}")
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

    def loop_jobcards(self):
        self.detect_jobcards()
        while self.jobcards_it.iterable:
            """2초 후에 다음 job-card를 클릭."""
            time.sleep(self.jobcard_click_secs)
            self.jobcards_it.nextop()
            self.parse_jobcard()
            self.collect_job_details()
            # break

class PaginationIterator:
    """동적으로 페이지 리스트가 변할 때 사용."""
    def __init__(self, driver, func, dbgon=True, avg_runtime=1):
        self.driver = driver
        self.start_dt = datetime.now().astimezone()
        self.dbgon = dbgon
        self.exp_runtime = avg_runtime
        self.func = func
        self.setup_pagination()
        """Pagination 이 존재하든 말든 초기 1회 무조건 실행."""
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

class JobsDriver(SearchConditionSetter, JobDetails, JobCards):

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
    nextpage_click_secs = 2
    jobcard_click_secs = 2
    job_details_human_reading_secs = 20

    def __init__(self, driver):
        self.driver = driver
        super().__init__()
        self.collect_dt = datetime.now().astimezone()

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

    def loop_pagination(self):
        self.pagination_it = PaginationIterator(self.driver, func=self.loop_jobcards)
        while self.pagination_it.iterable:
            self.pagination_it.nextop()
            """다음 페이지 버튼을 누르기까지 sleepsecs 만큼 걸린다."""
            time.sleep(self.nextpage_click_secs)
            # break

    def collect_on_keyword(self, keyword='machine learning', location='Spain', duration=0):
        fr = dbg.Function(inspect.currentframe()).report_init()
        ############################################################
        self.move_to_job_search_page()
        self.put_searching_keyword(keyword, location).choose_posted_duration(duration).set_sorting('date')
        ############################################################
        self.extract_keyword_location()
        self.loop_pagination()
        ############################################################
        fr.report_fin()

    def collect_on_keywords(self, search_keywords):
        fi = FunctionIterator(search_keywords, self.collect_on_keyword)
        while fi.iterable:
            fi.nextop()




#============================================================
"""Tester."""
#============================================================
