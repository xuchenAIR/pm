from pm4py.objects.log.importer.xes import factory as xes_import_factory
import pandas as pd
import streamlit as st
import alpha

def import_xes_with_time_sort(file):
    parameters = {"timestamp_sort": True}
    log = xes_import_factory.apply(file,
                                   # variant="nonstandard",
                                   parameters=parameters)
    return log
def import_xes(file):
    log = xes_import_factory.apply(file)
    return log


def get_log_from_xes_file(file):
    log = import_xes_with_time_sort(file)
    return Context(log)

class Context(object):
    log = []
    attributes = {}
    classifiers = {}
    extensions = {}
    present = {}
    obj_log = []
    df = None
    start_activities = {}
    end_activities = {}
    DEFAULT_NAME_KEY = 'concept:name'
    DEFAULT_TIMESTAMP_KEY = 'time:timestamp'
    DEFAULT_TRANSITION_KEY = 'lifecycle:transition'
    log_simple = None
    activities = None
    filtered_df = None
    is_filt_complete = False
    is_filt_start = False
    is_filt_end = False
    def __init__(self,log):
        self.log = log._list
        self.find_start_end_complete()
        self.attributes = log.attributes
        self.classifiers = log.classifiers
        self.extensions = log.extensions
        self.present = log.omni_present
        self.get_t_e_obj()
        self.get_df()
        self.log_simple = alpha.get_log_from_df(self.df)
        self.activities = alpha.get_all_activities(self.df)
        self.get_start_end()

    def find_start_end_complete(self):
        if 'concept:name' in self.log[0][0]:
            if self.log[0][0]['concept:name'] == 'Start':
                self.is_filt_start = True
            if self.log[0][-1]['concept:name'] == 'End':
                self.is_filt_end = True
        if 'lifecycle:transition' in self.log[0][0]:
            self.is_filt_complete = True

    def get_start_end(self):
        log_simple = self.log_simple
        for t in log_simple:
            if len(t) > 0:
                if t[0] not in self.start_activities:
                    self.start_activities[t[0]] = 0
                self.start_activities[t[0]] += 1
                if t[-1] not in self.end_activities:
                    self.end_activities[t[-1]] = 0
                self.end_activities[t[-1]] += 1


    def get_t_e_obj(self):
        for t in self.log:
            t_list = []
            for e in t:
                t_list.append(self.Event(e[self.DEFAULT_NAME_KEY],e[self.DEFAULT_TRANSITION_KEY],e[self.DEFAULT_TIMESTAMP_KEY]))
            self.obj_log.append(self.Trace(t.attributes,t_list))

    def get_df(self):
        df =  pd.DataFrame(data=None,columns=['case_id','activity','time','lifecycle'])
        row = 0
        for t in self.obj_log:
            for e in t.events:
                df.loc[row, 'case_id'] = t.attributes[self.DEFAULT_NAME_KEY]
                df.loc[row, 'activity'] = e.concept_name
                df.loc[row, 'time'] = pd.to_datetime(e.time_timestamp)
                df.loc[row, 'lifecycle'] = e.lifecycle_transition
                row += 1
        df = self.filt_start_end_complete(df)
        self.df = df

    def filt_start_end_complete(self,df):
        if self.is_filt_complete:
            df = df[df['lifecycle'] != 'complete']
        if self.is_filt_start:
            df = df[df['activity'] != 'Start']
        if self.is_filt_end:
            df = df[df['activity'] != 'End']
        return df




    class Event:
        concept_name = ''
        lifecycle_transition = ''
        time_timestamp = ''
        # classifier = ''
        def __init__(self,concept_name,lifecycle_transition,time_timestamp):
            self.concept_name = concept_name
            self.lifecycle_transition = lifecycle_transition
            self.time_timestamp = time_timestamp
            # self.classifier = classifier

    class Trace:
        attributes = {}
        events = []
        def __init__(self,attributes,events):
            self.attributes = attributes
            self.events = events




