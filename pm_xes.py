import streamlit as st
import pandas as pd
import PMTools
import Heuristic
import os
from graphviz import Digraph
import Miner_csv as Miner
import st.sidebar as side
import st.content as cont
import dealer_xes
import Miner_xes

FOLDER_DATA = 'data/'
st.title('Process Mining Tools For XES')
st.sidebar.title('一、选择文件：')

root = os.getcwd()
xes_list = PMTools.file_name_with_format(root+'\\data','.xes')
data_xes = st.sidebar.selectbox('1.选择分析的文件:',xes_list,key='import_data')



context = dealer_xes.get_log_from_xes_file(FOLDER_DATA+data_xes)
df = context.df
st.write('## 一、所选数据集（可筛查）：')
st.markdown('''
*提示：应用于算法的数据为过滤后数据集，此数据集仅供查询*
''')
st.sidebar.title('二、条件查询数据集：')

PMTools.select_data_set(df)


st.sidebar.title('三、数据过滤：')
#
#
min_time,max_time = PMTools.get_time_scole_from_fd(df)
parameters = {'time_filter':
                  [st.sidebar.date_input(label='日期过滤',key='date_start',value=min_time),
                   st.sidebar.date_input(label='日期过滤',key='date_end',value=max_time)]}

df_filterd_to_select = Miner_xes.filter_df(df,parameters)

context.filtered_df = df_filterd_to_select
#
# st.markdown('''
# ## 二、活动关系矩阵：
# ''')
# df = context.filt_start_end_complete(df)#除去start end complete
# matrix_AC = Miner_xes.get_matrix_AC(df)
# st.dataframe(matrix_AC)
#
#
st.markdown('''
## 三、统计：
''')
apply_stetistic = st.button('APPLY',key='apply_stetistic')
if apply_stetistic:
    obj_Stetistic = Miner.obj_Stetistic(df)
    obj_Stetistic.get_ac_frequency_plot()  # pie

    st.markdown('**轨迹长度**：')
    st.write('TRACE_LENGTH min: ', min(obj_Stetistic.event_num_per_case.values()))
    st.write('TRACE_LENGTH mean:', obj_Stetistic.mean_of_trace_length)
    st.write('TRACE_LENGTH max: ', max(obj_Stetistic.event_num_per_case.values()))
    obj_Stetistic.get_trace_lengh_plot()


st.markdown('''
## 四、过滤数据集
*提示：过滤后数据集为输入算法的最终数据。*
''')
df_filterd_to_select


st.markdown('''
## 五、Directly-Follow：
''')
directly_apply = st.button(label='Apply',key='open_Directly_Follow')
if directly_apply:
    Miner_xes.get_Directly_Follow(df,FOLDER_DATA+data_xes)
Miner_xes.get_Directly_Follow(df,FOLDER_DATA+data_xes)



st.markdown('''
## 六、Alpha Miner(Perit-Net)：
''')
alpha_apply = st.button(label='Apply',key='open_Perit_Net')
if alpha_apply:
    Miner_xes.Alpha_Miner_with_fiter(context.filtered_df,FOLDER_DATA+data_xes)
Miner_xes.Alpha_Miner_with_fiter(context.filtered_df,FOLDER_DATA+data_xes)



st.markdown('''
## 七、Heuristic(启发式)：
''')
import heuristic.hueristc_abstarct as hueristc_abstarct
parameters_hue = {hueristc_abstarct.DEPENDENCY_THRESH:0.5,
                  hueristc_abstarct.AND_MEASURE_THRESH:0.65,
                  hueristc_abstarct.MIN_ACT_COUNT:1,
                  hueristc_abstarct.MIN_DFG_OCCUR:1,
                  hueristc_abstarct.DFG_PRE_CLEAN_NOISE_THRESH:0.05,
                  hueristc_abstarct.LOOP_LENGTH_TWO_THRESH:0.5}

hueristic_apply = st.button('hueristic-net',key='hueristic')
if hueristic_apply:
    Heuristic.heuristic_net_xes(context,parameters['time_filter'][0],parameters['time_filter'][1],parameters_hue)