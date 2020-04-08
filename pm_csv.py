import streamlit as st
import pandas as pd
import PMTools
import alpha
import time
import os
from graphviz import Digraph
import Heuristic
import Miner_csv as Miner
import st.sidebar as side
import st.content as cont

FOLDER_DATA = 'data/'
st.title('Process Mining Tools For CSV')
st.sidebar.title('一、选择文件：')

root = os.getcwd()
csv_list = []





csv_list = PMTools.file_name_forCSV(root+'\\data')
data_csv = st.sidebar.selectbox('1.选择分析的文件(默认第一行为列名):',csv_list,key='import_data')
sep = st.sidebar.text_input('2.选择分隔符(默认英文分号)',value=';',key='seperate')

df = alpha.read_csv_to_dataframe(FOLDER_DATA+data_csv,sep=sep)


st.write('## 一、所选数据集（可筛查）：')
st.markdown('''
*提示：应用于算法的数据为过滤后数据集，此数据集仅供查询*
''')


st.sidebar.title('二、条件查询数据集：')


PMTools.select_data_set(df)




st.sidebar.title('三、数据过滤：')


min_time,max_time = PMTools.get_time_scole_from_fd(df)
parameters = {
'time_filter':[st.sidebar.date_input(label='日期过滤',key='date_start',value=min_time),
    st.sidebar.date_input(label='日期过滤',key='date_end',value=max_time)],
'resource_filter':st.sidebar.multiselect(label='执行者',options=PMTools.get_resource_from_df(df),key='resourece_filter')}

df_filterd = PMTools.filter_df(df,parameters)



# st.markdown('''
# ## 二、活动关系矩阵：
# ''')
# matrix_AC = Miner.get_matrix_AC(df)
# st.dataframe(matrix_AC)
#

st.markdown('''
## 三、统计：
''')
st.markdown('**活动频率**：')
obj_Stetistic = Miner.obj_Stetistic(df)
obj_Stetistic.get_ac_frequency_plot()#pie

st.markdown('**轨迹长度**：')
st.write('TRACE_LENGTH min: ',min(obj_Stetistic.event_num_per_case.values()))
st.write('TRACE_LENGTH mean:',obj_Stetistic.mean_of_trace_length)
st.write('TRACE_LENGTH max: ',max(obj_Stetistic.event_num_per_case.values()))
obj_Stetistic.get_trace_lengh_plot()


st.markdown('''
## 四、过滤数据集
*提示：过滤后数据集为输入算法的最终数据。*
''')
df_filterd


st.markdown('''
## 五、Directly-Follow：
''')
directly_apply = st.button(label='Apply',key='open_Directly_Follow')
if directly_apply:
    Miner.get_Directly_Follow(FOLDER_DATA+data_csv)




st.markdown('''
## 六、Alpha Miner(Perit-Net)：
''')
alpha_apply = st.button(label='Apply',key='open_Perit_Net')
if alpha_apply:
    Miner.Alpha_Miner_with_fiter(df_filterd,FOLDER_DATA+data_csv)





st.markdown('''
## 七、Heuristic(启发式)：
''')
# alpha_apply = st.button(label='Apply',key='open_Heuristic')
Heuristic.heuristic_net_csv(df_filterd)