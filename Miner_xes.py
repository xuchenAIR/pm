import alpha as alpha
from graphviz import Digraph
import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import PMTools
from pandas.tseries.offsets import *

DATA_DEBUG = 'data/activitylog_uci_detailed_labour.xes'
FOLDEER_PITRURE = 'picture/'

PARAMETER_TIME = 'time'
PARAMETER_SOURCE = 'source'
PARAMETERS = {PARAMETER_TIME:'time',PARAMETER_SOURCE:'source'}


def filter_df(df,parameters):
    if parameters is not None:
        df_filt = df
        min_time,max_time = PMTools.get_time_scole_from_fd(df)
        max_time = max_time.date()
        min_time = min_time.date()
        start_time = parameters['time_filter'][0]
        end_time = parameters['time_filter'][1]
        if min_time<=start_time<=max_time and min_time<=end_time<=max_time:
            pre = pd.to_datetime(start_time)
            des = pd.to_datetime(end_time)
            time = df['time']
            select = []
            for t in time:
                if pre <= t.tz_convert(None) <= des:
                    select.append(True)
                else:
                    select.append(False)
            df_filt = df[select]
        return df_filt
    return df


def drop_col_with_condition(df,col,val):
    row_list = df._stat_axis.values.tolist()
    for num in range(0,len(row_list)):
        if df.loc[num,col] == val:
            df.drop([num],inplace=True)
    return df

def select_sense_df(df):
    if 'lifecycle:transition' in df.columns.values.tolist():
        df = df[df['lifecycle'] != 'complete']
    filt_df = df[df['activity'] != 'Start']
    filt_df = filt_df[filt_df['activity'] != 'End']
    return filt_df


def get_matrix_AC(df):
    log = alpha.get_log_from_df(df)
    # 所有活动
    activities = alpha.get_all_activities(df)
    # 创建活动关系矩阵
    matrix_AC, list_Row, list_Col = alpha.get_activity_matrix(activities)
    alpha.initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col)
    alpha.check_parallel(matrix_AC, list_Row, list_Col)
    return matrix_AC


def get_Directly_Follow(df,data_file):
    ps = Digraph(name=FOLDEER_PITRURE+data_file.split('/')[1]+'_DF', node_attr={'shape': 'box'}, format='png')
    ps.graph_attr['rankdir'] = 'LR'
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




def Alpha_Miner_with_fiter(df,data_file):
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
    # 主要存储类
    alpha_miner = alpha.Alpha_Miner(start_set, end_set, log, causal, activities)
    # 获得pai
    alpha.get_pairs(alpha_miner)
    # 合并子类
    alpha.merge_subset(alpha_miner)
    # 删除子项
    alpha.delete_non_maximium_pair(alpha_miner)
    # 获得petri-net结构
    net, start_place, end_place = alpha.get_net(alpha_miner)
    # graphviz绘图
    Graph = alpha.graph()
    Graph.draw(net, start_place, end_place, decorations=None, parameters=None, data_name=data_file + '_Alpha')
