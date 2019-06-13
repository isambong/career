
from career import mongo_v2 as mongo
import pandas as pd
import inspect
from pandas.io.json import json_normalize


#============================================================
"""LinkedIn"""
#============================================================

def submodeling(obj, *args):
    submodel = "_".join(args)
    obj.submodel = f"{obj.modelname}__{submodel}"
    obj.tblname = obj.submodel
    return obj

class LinkedInJobPosting(mongo.Model):

    def __init__(self):
        super().__init__(__class__)
        self.inputs = ['search_keyword','search_location','collect_dt']
        self.output = ['html']
        jobcard = ['title','companyname','location']
        ############################################################
        self.collect_upsert_keys = self.inputs + jobcard

        ############################################################
        top_card = ['title','companyname','location','posted_time_ago','n_views','company_logo_url']
        job_summary = ['skills_match_ratio','n_applicants','job_level','n_employees','rng_employees','company_cate','connections']
        job_description = ['desc']
        job_description_details = ['seniority_level','industries','employment_type','job_functions']
        how_you_match = ['match_skills']
        applicant_insights = ['applicant_topskills','applicant_seniority_levels','applicant_educations','applicant_locations']
        company_insights = ['total_employees','company_growthrate','sector_growthrate','tenure']
        commute_aboutus = ['commute_addr','about_us']
        self.dt_cols = ['collect_dt','posted_time_ago','posted_dt']
        self.schema = self.inputs + self.output + self.dt_cols + jobcard + top_card + job_summary + job_description + job_description_details + how_you_match + applicant_insights + company_insights + commute_aboutus
        self.schema = list(set(self.schema))
        self.num_cols = ['n_views','skills_match_ratio','n_applicants','n_employees','total_employees','company_growthrate','sector_growthrate','tenure']
        self.listtype_cols = ['industries','job_functions','match_skills','applicant_topskills']
        self.dicstype_cols = ['connections','applicant_seniority_levels','applicant_educations','applicant_locations']
