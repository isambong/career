
"""
Version : 3
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
"""Collector
Version : 3
2019-05-29 기준,
LinkedIn 에서 25개 이상의 JobCards를 페이지 네비게이션 방식에서 Ajax기반의 스크롤 방식으로 변경했다.
따라서 version2에서 사용했던 Pagination 은 필요없고 version3에서는 Scroller를 새로 개발해야한다.
"""
#============================================================

class SearchCondition:
    """검색조건 설정."""

    def __init__(self, keywords_writing_secs=3, searchbutton_click_secs=1):
        # print(f"{'='*60}\n{self.__class__} | SearchCondition")
        super(SearchCondition, self).__init__()
        self.keywords_writing_secs = keywords_writing_secs
        self.searchbutton_click_secs = searchbutton_click_secs

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

    def extract_keyword_location(self):
        uo = urlparse(self.driver.current_url)
        qs = parse_qs(uo.query)
        self.search_keyword = qs['keywords'][0]
        self.search_location = qs['location'][0]

class JobDetails(models.LinkedInJobPosting):

    scroll_to_see_more_secs = 5
    scroll_to_premium_block_secs = 2
    job_details_human_reading_secs = 20
    job_details_ajax_waiting_secs = 3

    def __init__(self):
        # print(f"{'='*60}\n{self.__class__} | JobDetails")
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

    def click_job_description_see_more(self):
        """See More"""
        time.sleep(self.scroll_to_see_more_secs)
        job_description = self.driver.find_elements_by_class_name('jobs-description')
        see_more_btn = job_description[0].find_elements_by_class_name('artdeco-button')
        try:
            see_more_btn[0].click()
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 무시하라.")
            pass

    def click_applicant_insights_send_feedback(self):
        """Send Feedback"""
        time.sleep(self.scroll_to_premium_block_secs)
        applicant_insights = self.driver.find_elements_by_class_name('jobs-premium-applicant-insights')
        if len(applicant_insights) is 1:
            send_feedback = applicant_insights[0].find_elements_by_class_name('display-flex')
            if len(send_feedback) is 1:
                ActionChains(driver).move_to_element(send_feedback[0]).perform()
            else:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(send_feedback) is not 1.")
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n len(applicant_insights) is not 1.")

    def click_company_insights_more_company(self):
        """See more company insights"""
        time.sleep(self.scroll_to_premium_block_secs)
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

    def debug_re_search(self):
        print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n job_details_ajax_waiting_secs : {self.job_details_ajax_waiting_secs}")
        time.sleep(self.job_details_ajax_waiting_secs)
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
            self.click_job_description_see_more()
            self.click_applicant_insights_send_feedback()
            self.click_company_insights_more_company()
            self.debug_re_search()
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}")
            print(f"\n.\n.\n.\n {self.job_details_human_reading_secs}초 동안 job-details 읽는 척.\n.\n.\n.")
            time.sleep(self.job_details_human_reading_secs)
            self.save_job_details()
        else:
            pass

class JobCards(JobDetails):
    """필수불가결 액션.
    detect_jobcards.
    find_active_jobcard.
    parse_active_jobcard.
    click_next_jobcard.
    """
    def __init__(self):
        # print(f"{'='*60}\n{self.__class__} | JobCards")
        super().__init__()
        # super(JobCards, self)

    def inspect_jobcards(self):
        self.detect_jobcards().find_active_jobcard()

    def detect_jobcards(self):
        """HTML Tag class-hierarchy.
        jobs-search-two-pane__results
        jobs-search-results
        jobs-search-results__list
        """
        jobcard_ul = self.driver.find_elements_by_class_name('jobs-search-results__list')
        if len(jobcard_ul) is 1:
            self.jobcards = self.driver.find_elements_by_class_name('artdeco-list__item')
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Job-cards exist.\n jobcards_iterable : {self.jobcards_iterable}")
            return True
        else:
            print(f"\n len(jobcard_ul) is not 1.\n")
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Active-Jobcard 가 존재하지 않는 말도 안되는 상황.")
            return False
        return self

    def find_active_jobcard(self):
        if hasattr(self,'jobcards'):
            for i, jobcard in enumerate(self.jobcards):
                actives = jobcard.find_elements_by_class_name('job-card-search--is-active')
                if len(actives) is 1:
                    self.active_jobcard_num = i
                    self.active_jobcard = self.jobcards[i]
                    break
            if hasattr(self,'active_jobcard_num') is False:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n Active-Jobcard 가 존재하지 않는 말도 안되는 상황.")
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n hasattr(self,'jobcards') is False.")

    def click_next_jobcard(self):
        if hasattr(self,'active_jobcard_num'):
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n JobCard-Number {self.active_jobcard_num+1} 클릭.")
            self.jobcards[self.active_jobcard_num+1].click()
        else:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n hasattr(self,'active_jobcard_num') is False.")

    def parse_active_jobcard(self):
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

    def iter_jobcards(self):
        self.detect_jobcards()
        while self.jobcards_iterable:
            self.detect_jobcards()
            self.find_active_jobcard()
            self.parse_active_jobcard()
            self.collect_job_details()
            self.click_next_jobcard()

class JobsDriver(SearchCondition, JobCards):

    base_url = 'https://www.linkedin.com/jobs/search/'
    search_keywords = [
        'data analytics',
        'data analysis',
        'Data Scientist',
        'Data Science',
        # 'data engineer',
        'machine learning',
        'Artificial Intelligence (AI)',
        'natural language processing',
        'business intelligence (bi)',
        'python',
        'Node.js',
    ]

    def __init__(self, driver):
        # print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}")
        self.driver = driver
        super().__init__()

    def move_to_job_search_page(self):
        if re.search(self.base_url, string=self.driver.current_url) is None:
            print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 현재페이지가 Job Search page가 아니므로, 검색페이지로 이동.")
            self.driver.get(self.base_url)
        else:
            pass

    def is_readyto_collect(self):
        uo = urlparse(self.driver.current_url)
        if ('keywords' in uo.query) and ('location' in uo.query) and ('sortBy' in uo.query):
            return True
        else:
            return False

    def collect_on_keyword(self, keyword='machine learning', location='Spain', duration=0):
        fr = dbg.Function(inspect.currentframe()).report_init()
        ############################################################
        self.collect_dt = datetime.now().astimezone()
        self.move_to_job_search_page()
        self.put_searching_keyword(keyword, location).choose_posted_duration(duration).set_sorting('date')
        self.extract_keyword_location()
        ############################################################
        if self.is_readyto_collect:
            self.iter_jobcards()
        else:
            pass
        ############################################################
        fr.report_fin()

    def collect_on_keywords(self, search_keywords, location='Spain', duration=0):
        fr = dbg.Function(inspect.currentframe()).report_init()
        ############################################################
        fi = FunctionIterator(search_keywords, self.collect_on_keyword)
        while fi.iterable:
            fi.nextop()
        ############################################################
        fr.report_fin()

#============================================================
"""1차 Parser."""
#============================================================

class HTMLParser(models.LinkedInJobPosting):

    def __init__(self):
        super().__init__()
        self.change_schema()

    def change_schema(self):
        """파싱 후 저장할 컬럼만 스키마로 임시 설정."""
        self.parse_upsert_omit_keys = self.inputs + self.output
        for col in self.parse_upsert_omit_keys:
            if col in self.schema:
                self.schema.remove(col)
        print(f"{'='*60}\n{self.__class__} | {inspect.stack()[0][3]}")
        print(f" Changed schema len : {len(sorted(self.schema))}")
        print(f" Changed schema : {sorted(self.schema)}")
        return self

    def load_targets(self, filter=None):
        if filter is None:
            filter = {'html':{'$ne':None}, 'desc':None}
            # filter = {'html':{'$ne':None}}
        else:
            pass
        self.find(filter, {'_id':1, 'html':1})
        return self

    def detect_right_panel_v1(self, soup):
        view = soup.find('div', class_="job-view-layout")
        if view is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n job-view-layout is None.")
        else:
            main_content = view.find('div', class_="jobs-details__main-content")
            if main_content is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n jobs-details__main-content is None.")
            else:
                self.soup = main_content
        return self

    def detect_right_panel(self, soup):
        main_content = soup.find('div', class_="jobs-details__main-content")
        if main_content is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n jobs-details__main-content is None.")
        else:
            self.soup = main_content
        return self

    def top_card(self):
        """job-title, companyname, location, posted_time_ago, views"""
        s = self.soup.find('div', class_=re.compile('jobs-details-top-card\s'))
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-details-top-card' is None.")
        else:
            s = s.find('div', class_='jobs-details-top-card__container')
            if s is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n jobs-details-top-card__container is None.")
            else:
                self._company_logo(s)
                self._top_card_contents(s)
        return self

    def _company_logo(self, soup):
        s = soup.find('div', class_='jobs-details-top-card__company-logo-container')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-details-top-card__company-logo-container' is None.")
        else:
            img = s.find('img')
            if img is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'img-tag' is None.")
            else:
                # src="https://media.licdn.com/dms/image/C560BAQEkkhvIhl6aEg/company-logo_200_200/0?e=1566432000&amp;v=beta&amp;t=hrgzhpVIVx97S6LUp363YUqlqJ_vurRRDZaOjeGSnTg"
                if 'src' in list(img.attrs):
                    print(f"\n img.attrs :")
                    pp.pprint(img.attrs)
                    self.company_logo_url = img.attrs['src']
                    # r = requests.get(self.company_logo_url)
                    # print(f"\n r.status : {r.status}")


    def _top_card_contents(self, soup):
        s = soup.find('div', class_='jobs-details-top-card__content-container')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-details-top-card__content-container' is None.")
        else:
            title = s.find('h1', 'jobs-details-top-card__job-title')
            if title is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-details-top-card__job-title' is None.")
            else:
                self.title = title.get_text().strip()

            company_info = s.find('h3', 'jobs-details-top-card__company-info')
            if company_info is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-details-top-card__company-info' is None.")
            else:
                """##############################"""
                companyname = company_info.find('a')
                """##############################"""
                if companyname is None:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Top-Card__Company-Name' is None.")
                else:
                    self.companyname = companyname.get_text().strip()
                location = company_info.find('span', class_='jobs-details-top-card__bullet')
                if location is None:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Top-Card__Company-Location' is None.")
                else:
                    self.location = location.get_text().strip()

            info = s.find('p', class_='jobs-details-top-card__job-info')
            for string in info.stripped_strings:
                string = string.strip()
                if re.search('Posted\s*\d+',string=string) is not None:
                    self.posted_time_ago = string
                if re.search('\d+\s*views',string=string) is not None:
                    self.views = string
            return

    def job_summary(self):
        """3-boxes : Job, Company, Connections"""
        s = self.soup.find('div', class_=re.compile('^jobs-details-job-summary$'))
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n '^jobs-details-job-summary$' is None.")
        else:
            job_box = s.find('div',attrs={'data-test-job-summary-type':'job-list'})
            if job_box is None:
                print("s.find('div',attrs={'data-test-job-summary-type':'job-list'}) is None.")
            else:
                items = job_box.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if re.search('\d+ skills match$', string=text) is not None:
                        self.job_match_skills_ratio = text
                    if re.search('\d+ applicant[s]*', string=text) is not None:
                        self.job_applicants = text
                    if re.search('level$', string=text) is not None:
                        self.job_level = text

            company_box = s.find('div',attrs={'data-test-job-summary-type':'company-list'})
            if company_box is None:
                print("s.find('div',attrs={'data-test-job-summary-type':'company-list'}) is None.")
            else:
                items = company_box.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if re.search('\d+ employee[s]*', string=text) is not None:
                        self.company_employees = text
                    if len(item) is 2:
                        self.company_cate = text

            connection_box = s.find('div',attrs={'data-test-job-summary-type':"connections-list"})
            if connection_box is None:
                print("s.find('div',attrs={'data-test-job-summary-type':'connections-list'}) is None.")
            else:
                connections = []
                for atag in connection_box.find_all('a',attrs={'data-control-name':"jobdetails_sharedconnections"}):
                    connections.append({
                        'connection_cnt': atag.find('div',class_='job-flavors__label').get_text().strip(),
                        'connection_source': atag.find('img').attrs['title'],
                    })
                self.connections = connections
            return

    def _job_description_container(self):
        s = self.soup.find('div', class_=re.compile('^jobs-description'))
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n re.compile('^jobs-description') is None.")
        else:
            s = s.find('article',class_=re.compile('^jobs-description__container$'))
            if s is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n re.compile('^jobs-description__container') is None.")
            else:
                return s

    def job_description(self):
        s = self._job_description_container()
        s = s.find('div',class_='jobs-description-content__text')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n jobs-description-content__text is None.")
        else:
            self._recuiter_writing(s)
            self._job_description_details(s)
            return

    def _recuiter_writing(self, soup):
        s = soup.find('div',class_='justify-space-between')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'justify-space-between' is None.")
        else:
            s = s.find_next_sibling('span')
            if s is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n span tag is None.")
            else:
                self.desc = s.get_text().strip()

    def _job_description_details(self, soup):
        s = soup.find('div', class_='jobs-description-details')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'jobs-description-details' is None.")
        else:
            """Seniority Level"""
            seniority_level = s.find('h3',class_=re.compile('exp-title$'))
            if seniority_level is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Seniority Level' is None.")
            else:
                self.seniority_level = seniority_level.find_next_sibling('p').get_text().strip()

            """Industry"""
            industry_cats = s.find('h3',class_=re.compile('industries-title$'))
            if industry_cats is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Industry-Cate' is None.")
            else:
                industry_cats = industry_cats.find_next_sibling('ul')
                if industry_cats is None:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'industry_cats_ul' is None.")
                else:
                    self.industries = []
                    for li in industry_cats.find_all('li',class_='jobs-box__list-item'):
                        self.industries.append( li.get_text().strip() )

            """Employment Type"""
            employment_type = s.find('h3',class_=re.compile('employment-status-title$'))
            if employment_type is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Employment Type' is None.")
            else:
                self.employment_type = employment_type.find_next_sibling('p').get_text().strip()

            """Job Functions"""
            job_functions = s.find('h3',class_=re.compile('job-functions-title$'))
            if job_functions is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Job Functions' is None.")
            else:
                job_functions = job_functions.find_next_sibling('ul')
                if job_functions is None:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'job_functions' is None.")
                else:
                    self.job_functions = []
                    for li in job_functions.find_all('li',class_='jobs-box__list-item'):
                        self.job_functions.append( li.get_text().strip() )

    def how_you_match(self):
        s = self._job_description_container()
        hym = s.find('div', class_=re.compile('^jobs-ppc-quality$'))
        if hym is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'How you match' is None.")
        else:
            skills_block = hym.find('div', class_=re.compile('^jobs-ppc-quality__content$'))
            if skills_block is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Skills'(block) is None.")
            else:
                self.match_skills = []
                for li in skills_block.find_all('li'):
                    self.match_skills.append( li.find('span',class_='jobs-ppc-criteria__value').get_text().strip() )

    def competitive_intelligence_about_applicants(self):
        s = self.soup.find('div', class_=re.compile('jobs-premium-applicant-insights\s*'))
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n re.compile('jobs-premium-applicant-insights\s') is None.")
        else:
            """Applicants for this job"""

            """Top skills"""
            top_skills = s.find('div',class_='top-skills')
            if top_skills is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Top skills' is None.")
            else:
                self.applicant_topskills = []
                for li in top_skills.find_all('li'):
                    if li.find('span') is not None:
                        li.span.decompose()
                    for string in li.stripped_strings:
                        self.applicant_topskills.append(string.strip())

            """Seniority level"""
            applicant_levels = s.find('div',class_='applicant-experience')
            if applicant_levels is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Seniority level' is None.")
            else:
                self.applicant_levels = []
                for li in applicant_levels.find_all('li'):
                    p = li.p.get_text().strip()
                    m = re.match('\d+',string=p)
                    self.applicant_levels.append({
                        'count': p[m.start():m.end()],
                        'lvname': p[m.end():].replace(' applicants','').strip(),
                        'max_cnt': li.progress.attrs['max'],
                        'now_cnt': li.progress.attrs['value'],
                    })

            """Education"""
            applicant_educations = s.find('div',class_='applicant-education')
            if applicant_educations is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Education' is None.")
            else:
                self.applicant_educations = []
                for li in applicant_educations.find_all('li'):
                    app_education = {}

                    for span in li.find_all('span',class_=re.compile('^jobs[a-z\s-]+__list')):

                        text = span.get_text().strip()
                        if re.search('\d+', string=text) is not None:
                            app_education.update({'ratio':text})
                        if re.search('^have', string=text) is not None:
                            app_education.update({'degree':text})
                    if len(list(app_education)) is not 0:
                        self.applicant_educations.append(app_education)

            """Location"""
            applicant_locations = s.find('div',class_=re.compile('jobs-premium-applicant-insights__top-locations\s'))
            if applicant_locations is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Location' is None.")
            else:
                self.applicant_locations = []
                for li in applicant_locations.find_all('li'):
                    app_location = {}
                    location = li.find('p',class_=re.compile('top-locations-title\s'))
                    if location is not None:
                        app_location.update({'location':location.get_text().strip()})
                    count = li.find('p',class_=re.compile('top-locations-details\s'))
                    if count is not None:
                        count = count.find('span')
                        if count is not None:
                            app_location.update({'count':count.get_text().strip()})
                    if len(list(app_location)) is not 0:
                        self.applicant_locations.append(app_location)
            return

    def insight_look_at_company(self):
        s = self.soup.find('div', class_=re.compile('jobs-premium-company-insights[\s]*'))
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n re.compile('jobs-premium-company-insights\s*') is None.")
        else:
            """Hiring trends over the last 2 years"""
            hiring_trend = s.find('div',class_=re.compile('hiring-trends'))
            if hiring_trend is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Hiring trends over the last 2 years' is None.")
            else:
                for li in hiring_trend.find_all('li',class_='jobs-premium-company-growth__stat-item'):
                    mixed_txt = li.get_text().strip()
                    if re.search('Total employee[s]*',string=mixed_txt, flags=re.I) is not None:
                        m = re.search('[0-9,]+',string=mixed_txt)
                        if m is not None:
                            self.total_employees = mixed_txt[m.start():m.end()].strip()
                    elif re.search('Company-wide',string=mixed_txt, flags=re.I) is not None:
                        if True:
                            self.company_growth = li.find('span', class_='visually-hidden').get_text().strip()
                        else:
                            m = re.search('\d+%\s*[a-z]*',string=mixed_txt)
                            if m is not None:
                                self.company_growth = mixed_txt[m.start():m.end()].strip()
                    else:
                        if True:
                            self.sector_growth = li.find('span', class_='visually-hidden').get_text().strip()
                        else:
                            m = re.search('\d+%\s*[a-z]*',string=mixed_txt)
                            if m is not None:
                                self.sector_growth = mixed_txt[m.start():m.end()].strip()

                """Average tenure"""
                tenure = hiring_trend.find('span',class_="jobs-premium-company-growth_average-tenure")
                if tenure is None:
                    print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'Average tenure ' is None.")
                else:
                    self.tenure = tenure.find(string=re.compile('[\.\d+]+\s*year[s]*')).strip()
            return self

    def commute(self):
        s = self.soup.find(id='commute-module')
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'See your commute' is None.")
        else:
            address = s.find('div',class_=re.compile('^jobs-commute-module__company-location$'))
            if address is None:
                print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'address' is None.")
            else:
                self.company_addr = address.get_text().strip()

    def about_us(self):
        s = self.soup.find(id="company-description-text")
        if s is None:
            print(f"{'#'*60}\n{self.__class__} | {inspect.stack()[0][3]}\n 'About Us' is None.")
        else:
            self.aboutus = s.get_text().strip()

    def parse(self):
        loop = dbg.Loop(f"{self.__class__} | {inspect.stack()[0][3]}", len(self.docs))
        for d in self.docs:
            self.attributize(d)
            soup = BeautifulSoup(d['html'], 'html.parser')
            self.detect_right_panel(soup)
            self.top_card()
            self.job_summary()
            self.job_description()
            self.how_you_match()
            self.competitive_intelligence_about_applicants()
            self.insight_look_at_company()
            self.commute()
            self.about_us()
            self.update_doc({'_id':d['_id']}, False)
            # break
            loop.report()

def parse(filter=None):
    p = HTMLParser()
    p.load_targets(filter)
    p.parse()

#============================================================
"""2차 Parser."""
#============================================================

class DataColumnsParser(models.LinkedInJobPosting):

    def __init__(self):
        super().__init__()

    def load_targets(self, filter=None):
        projection = self.schema.copy()
        needless = self.inputs + self.output
        needless.remove('collect_dt')
        for e in needless:
            if e in projection:
                projection.remove(e)
        projection = {e:1 for e in projection}
        self.find(filter, projection)

    def clean(self, df):
        df = self.clean_dtcols(df)
        df = self.clean_numcols(df)
        return df

    def clean_dtcols(self, df):
        """날짜문자열을 날짜타입으로 변환"""
        def _clean_posted_time_ago(posted_time_ago):
            if isinstance(posted_time_ago, str) and len(posted_time_ago) > 0:
                m = re.search('\d+',string=posted_time_ago)
                if m is None:
                    print(f" m is None.\n posted_time_ago : {posted_time_ago}")
                else:
                    num = int(posted_time_ago[m.start():m.end()])
                    if 'second' in posted_time_ago:
                        return timedelta(seconds=num)
                    elif 'minute' in posted_time_ago:
                        return timedelta(minutes=num)
                    elif 'hour' in posted_time_ago:
                        return timedelta(hours=num)
                    elif 'day' in posted_time_ago:
                        return timedelta(days=num)
                    elif 'week' in posted_time_ago:
                        return timedelta(weeks=num)
                    elif 'month' in posted_time_ago:
                        return timedelta(days=num*30.5)
                    elif 'year' in posted_time_ago:
                        return timedelta(days=num*365)
                    else:
                        print(f"{'#'*60}\n{inspect.stack()[0][3]}\n 이런 경우는 발생할 수 없다.\n posted_time_ago : {posted_time_ago}")

        # 수집일시, 포스팅시간정보 둘 중에 하나라도 없으면 계산불가.
        dtdf = df.reindex(columns=self.dt_cols+['_id']).dropna(axis=0, how='any')
        # len(dtdf)
        # dtdf.tail()
        dtdf.posted_time_ago = dtdf.posted_time_ago.apply(_clean_posted_time_ago)
        # dtdf.head()
        # dtdf.sort_values('posted_time_ago',ascending=False)
        # dtdf.info()
        dtdf['posted_dt'] = dtdf.collect_dt - dtdf.posted_time_ago
        self.dt_cols += ['posted_dt']
        # dtdf.sort_values('posted_dt',ascending=False)
        return pd.merge(df, dtdf, on='_id')

    def clean_numcols(self, df):
        numdf = df.reindex(columns=self.num_cols+['_id']).dropna(axis=0, how='all')
        numdf = self._clean_ratio_cols(numdf)
        numdf = self._clean_comma_number_cols(numdf)
        # return pd.merge(df, numdf, on='_id')
        return numdf

    def _clean_ratio_cols(self, numdf):
        """비율 Ratio 변환"""
        def _clean_growth_col(x):
            if isinstance(x,str):
                if x.isnumeric():
                    return float(x)/100
                else:
                    return None
            elif isinstance(x,int):
                return float(x/100)
            elif isinstance(x,float):
                return x/100
            else:
                return None

        updown_p = re.compile('(in|de)crease', flags=re.I)
        def _clean_growth_addi_col(x):
            if isinstance(x,str):
                if updown_p.search(string=x) is None:
                    return None
                else:
                    return x.strip()
            else:
                return None

        for col in ['company_growth','sector_growth']:
            addi_col = f"{col}_updown"
            growdf = numdf[col].str.extract(pat=r'(\d+)\%\s*(.*)').rename(columns={0:col,1:addi_col})
            numdf.update(growdf)
            growdf1 = growdf.reindex(columns=[addi_col])
            numdf = numdf.join(growdf1)
            numdf[col] = numdf[col].apply(_clean_growth_col)
            numdf[addi_col] = numdf[addi_col].apply(_clean_growth_addi_col)
        return numdf

    def _clean_comma_number_cols(self, numdf):
        """콤마숫자 변환"""
        numdf.total_employees = numdf.total_employees.apply(lambda x: x if x is np.nan else int(x.replace(',','')))
        return numdf
