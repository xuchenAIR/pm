import streamlit as st
import os
import PMTools

st.title('Data File Manager of Process Mining')

st.sidebar.title('工具栏')




st.sidebar.title('缓存图片处理：')
# st.sidebar.selectbox('已有图片')
is_reset = st.sidebar.button('重置缓存集',key='reset_piture')
Picture_Folder = 'picture'
if is_reset:
    if os.path.exists(Picture_Folder):
        pics = PMTools.file_name_all(Picture_Folder+'\\')
        for pic in pics:
            os.remove(Picture_Folder+'\\'+pic)




st.markdown('''
## 一、导入数据文件(csv/xes)
*提示：请先填写文件名并上传文件之后点击UPLOAD(目前暂时支持csv和xes格式的文件)，上传之后请刷新页面*
''')
file_name = st.text_input('Step 1: input the upload file name:',key='imput_file_name')
upload_file = st.file_uploader('Step 2: upload your data file(csv/xes)',key='upload_file',type=['csv','xes'])
is_upload =  st.button('UPLOAD',key='upload_button')
if is_upload:
    if file_name=='' or file_name is None or upload_file is None:
        st.warning('请输入文件名并上传文件！')
    # elif ~(file_name.endswith('.csv') or file_name.endswith('.xes')):
    #     st.warning('请上传csv或xes格式的文件！')
    elif (file_name.endswith('.csv') or file_name.endswith('.xes')) and ~(file_name=='' or file_name is None or upload_file is None):
        PMTools.upload_file(file_name,upload_file)

st.markdown('''
## 二、删除数据文件
*提示：file_name：文件名、size：文件大小/M、atime：访问时间、ctime：创建时间、mtime：最近修改时间*
''')
root = os.getcwd()
xes_list = PMTools.file_name_with_format(root+'\\data','.xes')
csv_list = PMTools.file_name_with_format(root+'\\data','.csv')

xes_df = PMTools.get_file_df(xes_list)
csv_df = PMTools.get_file_df(csv_list)
st.dataframe(xes_df)
st.dataframe(csv_df)

remove_list = [
st.multiselect('选择删除的xes文件：',xes_list,key='remove_xes_list'),
st.multiselect('选择删除的csv文件：',csv_list,key='remove_csv_list')]

st.markdown('''
*提示：删除之后请刷新页面。(请谨慎删除)*
''')

is_remove = st.button('REMOVE',key='remove_button')
if is_remove:
    if remove_list[0] !=[] and remove_list[1] !=[]:
        PMTools.delete_files(remove_list[0],'data\\')
        PMTools.delete_files(remove_list[1], 'data\\')
        st.success('remove sucessfully')
        st.balloons()
    elif remove_list[0] !=[] and remove_list[1] ==[]:
        PMTools.delete_files(remove_list[0],'data\\')
        st.success('remove sucessfully')
        st.balloons()
    elif remove_list[0] ==[] and remove_list[1] !=[]:
        PMTools.delete_files(remove_list[1],'data\\')
        st.success('remove sucessfully')
        st.balloons()
    else:
        st.warning('选择文件后再点击删除！')
