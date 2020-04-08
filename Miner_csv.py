import alpha as alpha
from graphviz import Digraph
import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
DATA_DEBUG = 'data/running-example.csv'
FOLDEER_PITRURE = 'picture/'

PARAMETER_TIME = 'time'
PARAMETER_SOURCE = 'source'
PARAMETERS = {PARAMETER_TIME:'time',PARAMETER_SOURCE:'source'}


def Alpha_Miner_with_fiter(df,data_file):
    Graph = alpha.graph()
    log = alpha.get_log_from_df(df)
    # 所有活动
    activities = alpha.get_all_activities(df)
    # 创建活动关系矩阵
    matrix_AC, list_Row, list_Col = alpha.get_activity_matrix(activities)
    # 把log中活动关系填入矩阵
    start_set, end_set = alpha.initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col)
    # 更新并行关
    parallel_list = alpha.check_parallel(matrix_AC, list_Row, list_Col)
    # 因果关系-set
    causal = alpha.get_causal(log)
    # 平行关系-set
    parallel = alpha.get_parallel(parallel_list)
    # 主要存储类
    alpha_miner = alpha.Alpha_Miner(start_set, end_set, log, causal, activities)
    # 获得pai
    alpha.get_pairs(alpha_miner)
    # 合并子类
    alpha.merge_subset(alpha_miner)
    # 获得place
    alpha.delete_non_maximium_pair(alpha_miner)
    # 获得petri-net结构
    net, start_place, end_place = alpha.get_net(alpha_miner)
    # graphviz绘图
    Graph.draw(net, start_place, end_place, decorations=None, parameters=None, data_name=data_file + '_Alpha')


def get_matrix_AC(df):
    log = alpha.get_log_from_df(df)
    # 所有活动
    activities = alpha.get_all_activities(df)
    # 创建活动关系矩阵
    matrix_AC, list_Row, list_Col = alpha.get_activity_matrix(activities)
    alpha.initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col)
    alpha.check_parallel(matrix_AC, list_Row, list_Col)
    return matrix_AC

def Alpha_Miner(data_file=DATA_DEBUG, sep=';', time_format='%d-%m-%Y:%H.%M'):
    '''
    alpha algorithm
    :return:
    '''
    Graph = alpha.graph()
    df = alpha.read_csv_to_dataframe(data_name=data_file,sep=sep,time_format=time_format)
    # 日志
    log = alpha.get_log_from_df(df)
    # 所有活动
    activities = alpha.get_all_activities(df)
    # 创建活动关系矩阵
    matrix_AC, list_Row, list_Col = alpha.get_activity_matrix(activities)
    # 把log中活动关系填入矩阵
    start_set, end_set = alpha.initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col)
    # 更新并行关
    parallel_list = alpha.check_parallel(matrix_AC, list_Row, list_Col)
    # 因果关系-set
    causal = alpha.get_causal(log)
    # 平行关系-set
    parallel = alpha.get_parallel(parallel_list)
    # 主要存储类
    alpha_miner = alpha.Alpha_Miner(start_set, end_set, log, causal, activities)
    # 获得pai
    alpha.get_pairs(alpha_miner)
    # 合并子类
    alpha.merge_subset(alpha_miner)
    # 获得place
    alpha.delete_non_maximium_pair(alpha_miner)
    # 获得petri-net结构
    net, start_place, end_place = alpha.get_net(alpha_miner)
    # graphviz绘图
    viz = Graph.draw(net, start_place, end_place, decorations=None, parameters=None, data_name=data_file+'_Alpha')
    return viz,matrix_AC


def get_Directly_Follow(data_file=DATA_DEBUG, sep=';', time_format='%d-%m-%Y:%H.%M'):
    ps = Digraph(name=FOLDEER_PITRURE+data_file.split('/')[1]+'_DF', node_attr={'shape': 'box'}, format='png')
    ps.graph_attr['rankdir'] = 'LR'
    df = alpha.read_csv_to_dataframe(data_name=data_file, sep=sep, time_format=time_format)
    activities = alpha.get_all_activities(df)
    log = alpha.get_log_from_df(df)
    matrix_AC, list_Row, list_Col = alpha.get_activity_matrix(activities)
    alpha.initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col)
    for dnode in activities:
        ps.node(dnode)
    for x in range(0, matrix_AC.shape[0]):
        for y in range(0, matrix_AC.shape[1]):
            if matrix_AC.loc[list_Row[x], list_Col[y]] == '->':
                ps.edge(list_Row[x], list_Col[y])
    ps.view()

class obj_Stetistic(object):
    df = ''
    log = ''
    case_num = 0
    event_num = 0
    event_class = 0
    activities = []
    event_num_per_case = {}#轨迹长度 case_id:len
    activities_count = {}
    mean_of_trace_length = 0
    mean_of_ac_frequency = 0#活动出现频率平均值
    account_ac_all = 0#活动总数

    def get_trace_lengh_plot(self):
        y = list(self.event_num_per_case.keys())
        x = list(self.event_num_per_case.values())
        # get_horizontal_bar_chart(y,x)
        mod  = pd.DataFrame(data=None, index=y)
        for i in y:
            mod.loc[i,0] = self.event_num_per_case[i]
        st.bar_chart(mod)
        st.text('x : CASE_ID / y : TRACE_LENGTH')

    def get_ac_frequency_plot(self):
        y = list(self.activities_count.keys())
        x = list(self.activities_count.values())
        self.mean_of_ac_frequency = self.event_num / len(x)
        mod = pd.DataFrame(data=None, index=y)
        for i in y:
            mod.loc[i, 0] = self.activities_count[i]
        st.bar_chart(mod)
        st.text('x : ACTIVITY / y : FREQUENCY')

    def __init__(self,df):
        self.df = df
        self.log = alpha.get_log_from_df(df)
        if self.log != '':
            self.case_num = len(self.log)

            for trace in self.log:
                for event in trace:
                    self.activities_count[event] = 0

            for trace in self.log:
                self.event_num += len(trace)


            self.activities = alpha.get_all_activities(df)
            self.event_class = len(self.activities)

            for i in df.drop_duplicates(['case_id']).case_id:
                self.event_num_per_case[i] = 0

            for i in df.drop_duplicates(['case_id']).case_id:
                self.event_num_per_case[i] = len(df[df['case_id']==i])


            self.mean_of_trace_length = self.event_num/len(self.event_num_per_case)


            for trace in self.log:
                for event in trace:
                    self.activities_count[event] += 1

def get_plot(x,y,xlabel,ylabel,title):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y,scaley=False)
    st.pyplot()

def get_pie(data,ingredients):
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    def func(pct, allvals):
        absolute = int(pct / 100. * np.sum(allvals))
        return "{:.1f}%".format(pct)
    wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                      textprops=dict(color="w"))
    plt.setp(autotexts, size=5, weight="bold")
    ax.legend(wedges, ingredients,
              title="Activity",
              loc="center right",
              bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title("event_frequency")
    st.pyplot()

def get_horizontal_bar_chart(y,x):
    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = np.arange(len(y))

    # error = np.random.rand(len(y))

    ax.barh(y_pos, x, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylabel('case_id')
    ax.set_xlabel('every trace\'s length')
    ax.set_title('trace_length')

    st.pyplot()

