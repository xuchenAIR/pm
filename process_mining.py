import streamlit as st
import numpy as np
import pandas as pd

st.title('Process Mining Tools For CSV')
st.sidebar.title('工具栏：')
import time
import os
root = os.getcwd()
csv_list = []
def file_name(file_dir):
    csv_list = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_list.append(file)
    return csv_list
csv_list = file_name(root+'\\data')


import PMTools
root = PMTools.Get_Dir.root


data_csv = st.sidebar.selectbox('1.选择分析的文件:',csv_list)



uploaded_file = st.sidebar.file_uploader("临时加载新的csv文件(不会添加到资源管理器)", type="csv")
if uploaded_file is not None:
     data = pd.read_csv(uploaded_file,header=0,sep=';')
     data
# st.write('# 步骤1:')



df = pd.read_csv('data/'+data_csv,header=0,sep=';')
df.columns = ["case_id","event_id","time","activity","resource","costs"]
df["time"] = pd.to_datetime(df.time,format="%d-%m-%Y:%H.%M")
# df.head(50)
st.write('## 1.所选数据集的部分数据')
df





#第一步 确定流程图的结构
list_all_AC = []
for ac in df['activity']:#取所有的activity，（去重）作为矩阵的行列
    list_all_AC.append(ac)
    
list_all_AC = list(set(list_all_AC))


list_activity = [] # 所有流程的幂集

for i in df.drop_duplicates(['case_id']).case_id:#每一组caseID进行遍历，时间升序排列，汇聚成list，去重
    case_AC = ''
    for ac in df[df['case_id'].isin([i])].sort_values('time',ascending=True).activity:
        case_AC += ac + ';'
    list_activity.append(case_AC[:-1])

list_activity = list(set(list_activity))





matrix_AC = pd.DataFrame(data=None,columns=list_all_AC,index=list_all_AC) #所有活动的矩阵

list_Row = matrix_AC._stat_axis.values.tolist() # 行名称
list_Col =  matrix_AC.columns.values.tolist()    # 列名称
# matrix_AC




def Zero(matrix):#初始化0
    for x in range(0,matrix.shape[0]):
        for y in range(0,matrix.shape[1]):
            matrix_AC.loc[list_Row[x],list_Col[y]]=0




def PerCase(case):#对每组case取出矩阵
    for x in range(0,len(case)-1):
        matrix_AC.loc[case[x],case[x+1]] += 1



# 第二步 填入任务表
Zero(matrix_AC)
for every_case in list_activity: #每组caseID下的活动顺序信息填入矩阵中
    every_case = every_case.split(sep=';')#list
    PerCase(every_case)

st.write('## 任务关系表')
matrix_AC




list_parallel = []#所有并行的任务对
def check_parallel(matrix):#检测并行,并行的值置为0
    for x in range(0,matrix.shape[0]):#初始化0
        for y in range(0,x+1):
            if matrix_AC.loc[list_Row[x],list_Col[y]]>0 and matrix_AC.loc[list_Col[y],list_Row[x]]>0:# 并行任务
                list_parallel.append([list_Row[x],list_Col[y]])
                matrix_AC.loc[list_Row[x],list_Col[y]] = 0
                matrix_AC.loc[list_Col[y],list_Row[x]] = 0
check_parallel(matrix_AC)
# matrix_AC
# print(list_parallel)




from graphviz import Digraph



ps = Digraph(name='process-mining', node_attr={'shape': 'box'},format='pdf')
ps.graph_attr['rankdir'] = 'LR'
def input_matrix(matrix):
    for dnode in list_all_AC:
        ps.node(dnode)
    for x in range(0,matrix.shape[0]):
        for y in range(0,matrix.shape[1]):
            if matrix.loc[list_Row[x],list_Col[y]] > 0:
                ps.edge(list_Row[x],list_Col[y])

input_matrix(matrix_AC)
# ps.view()



st.write('## 任务流程模型：')
ps

if st.button('游览或保存图片'):
    ps.view()
st.markdown('''
    *说明：如需保存图片可点击按钮通过查看器保存副本到指定位置。*
    ''')

