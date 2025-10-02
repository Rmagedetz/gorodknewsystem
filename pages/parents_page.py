import streamlit as st
import sql

df = sql.Parent.get_df()

show = st.dataframe(df,
                    column_config={'id':'ID',
                                   'parent_name':'ФИО Родителя',
                                   'parent_phone':'Тел.',
                                   'email':'email'},
                    hide_index=True)