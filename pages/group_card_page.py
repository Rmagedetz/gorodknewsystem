import pandas as pd
import streamlit as st
import sql

groups_df = sql.Groups.get_df()
permission = st.session_state.user_permissions['editing_groups'][0]

left, center, right = st.columns(3)

seasons = sql.Seasons.get_df()['season_name']
with left:
    season_selector = st.selectbox('Сезон', seasons)

filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
with center:
    filial_selector = st.selectbox('Филиал', filials)

groups = sql.Groups.get_df(season_name=season_selector,
                           filial_name=filial_selector)['group_name']

with right:
    group_selector = st.selectbox('Группа', groups)

records_df = sql.Records.get_df(season_name=season_selector,
                                filial_name=filial_selector,
                                group_name=group_selector)

parents_df = sql.Parent.get_df()
childrens_df = sql.Child.get_df()

merged = records_df.merge(parents_df, on='parent_name', how='left')
merged = merged.merge(childrens_df, on='child_name', how='left')

merged = merged[['child_name', 'child_age', 'parent_name_x', 'parent_phone', 'record_status', 'comment']]
for day in range(1, 11):
    merged[day] = ''
show = st.data_editor(merged,
                      column_config={
                          'child_name': 'ФИО Ребенка',
                          'child_age': 'Возраст',
                          'parent_name_x': 'ФИО Родителя',
                          'parent_phone': 'Тел. родителя',
                          'record_status': 'Оплата',
                          'comment': 'Комменарий'
                      },
                      hide_index=True)
