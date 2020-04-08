import streamlit as st
import pandas as pd
import os

def file_name_all(file_dir):
    file_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            file_list.append(file)
    return file_list

def file_name_with_format(file_dir,format):
    format_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if file.endswith(format):
                format_list.append(file)
    return format_list

def file_name_forCSV(file_dir):
    csv_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_list.append(file)
    return csv_list


def select_data_set(df):
    list_Row = df._stat_axis.values.tolist()  # 行名称
    list_Col = df.columns.values.tolist()  # 列名称

    select_cols = st.sidebar.multiselect('1.筛选列名：', list_Col, key='list_Col')

    scole = [
        st.sidebar.number_input('2.最小行数(最小行不能超过最大行)', min_value=0, max_value=list_Row[-1], key='num_min', value=0),
        st.sidebar.number_input('最大行数', min_value=0, max_value=list_Row[-1], key='num_max', value=list_Row[-1])
    ]

    x = min(list_Row[-1], scole[0])
    x = max(0, x)
    y = min(list_Row[-1],scole[1])
    y = max(0,y)
    if (x <= y) and (select_cols != []):
        st.dataframe(df[select_cols].loc[x:y, select_cols])
    elif (x <= y) and (select_cols == []):
        st.dataframe(df.loc[x:y])
    elif (x > y) and (select_cols != []):
        st.dataframe(df[select_cols])
    else:
        st.dataframe(df)

def get_resource_from_df(df):
    return list(df.drop_duplicates(['resource']).resource)

def get_time_scole_from_fd(df):
    return pd.to_datetime(min(df['time'])),pd.to_datetime(max(df['time']))

from pandas.tseries.offsets import *
def filter_df(df,parameters):
    if parameters is not None:
        min_time,max_time = get_time_scole_from_fd(df)
        max_time = max_time.date()
        min_time = min_time.date()
        start_time = parameters['time_filter'][0]
        end_time = parameters['time_filter'][1]
        if min_time<=start_time<=max_time and min_time<=end_time<=max_time:
            pre = pd.to_datetime(start_time)
            df = df[pre<=df['time']]
            des = pd.to_datetime(end_time) + 1 * BDay()
            df = df[df['time']<=des]
        resource = parameters['resource_filter']
        # resource = ['Ellen']
        if len(resource)>0:
            all_resource = get_resource_from_df(df)
            found_resource = []
            for s in all_resource:
                if s not in resource:
                    found_resource.append(s)
            df = df[df.resource.isin(found_resource)]
        return df










class Get_Dir:
    '路径管理'
    root = '' #'本文件当前路径'
    def __init__(self):
        root = os.getcwd()

    def get_path_file(self,dirs):
        return os.path.join(x for x in dirs)

    '获取指定路径所有文件'
    def file_name(self,file_dir):
        list_files = []
        list_dirs = []
        list_root = []
        for root, dirs, files in os.walk(file_dir):
            list_files.append(files)
            list_dirs.append(dirs)
            list_root.append(root)
        return list_files.pop(0),list_dirs.pop(0),list_root.pop(0)


def upload_file(file_name,upload_file):
    if os.path.exists("data\\"+file_name):
        st.warning('文件已存在，请更改文件名！')

    else:
        if file_name.endswith('.csv') and (upload_file.getvalue().find('xml', 0, 40) > -1):
            st.error('检测出xml格式数据，请更改后缀名为.xes！')
        elif file_name.endswith('.xes') and (upload_file.getvalue().find('xml', 0, 40) == -1):
            st.error('未检测出xml格式数据，请更改后缀名为.csv！')
        elif file_name.endswith('.csv') and (upload_file.getvalue().find('xml', 0, 40) == -1):
            wrt_to_file("data\\" + file_name, upload_file)
        elif file_name.endswith('.xes') and (upload_file.getvalue().find('xml', 0, 40) >-1):
            wrt_to_file("data\\" + file_name,upload_file)



def wrt_to_file(file_name,upload_file):
    with open(file_name, 'w') as file_object:
        file_object.write(upload_file.getvalue())
        file_object.close()
        st.success('upload secessfully')
        st.balloons()


import time
def get_file_df(file_list):
    collumns = ['file_name','size','atime','ctime','mtime']
    file_df = pd.DataFrame(data=None,columns=collumns)
    num = 0
    for file in file_list:
        statinfo = os.stat("data\\"+file)
        dir_file = "data\\"+file
        file_df.loc[num,'file_name'] = file
        file_df.loc[num, 'size'] = statinfo.st_size/1024
        file_df.loc[num, 'atime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(dir_file).st_atime))
        file_df.loc[num, 'ctime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(dir_file).st_ctime))
        file_df.loc[num, 'mtime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(dir_file).st_mtime))
        num += 1
    return  file_df

def delete_files(file_list,folder):
    for file in file_list:
        os.remove(folder+file)