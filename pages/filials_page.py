import streamlit as st
import sql

filials_df = sql.Filials.get_df()
permission = st.session_state.user_permissions['editing_filials'][0]

st.dataframe(filials_df, column_config={
    'filial_id': st.column_config.Column('ID'),
    'season_name': st.column_config.Column('Название сезона'),
    'filial_name': st.column_config.Column('Название филиала'),
}, hide_index=True)


@st.dialog('Добавить филиал')
def add_filial():
    seasons_df = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons_df)
    filial_name = st.text_input('Название филиала')
    if st.button('Добавить филиал', key='add_filial_accept'):
        sql.Filials.add_record(
            season_name=season_selector,
            filial_name=filial_name
        )
        st.rerun()


@st.dialog('Удалить филиал')
def del_filial():
    seasons_df = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons_df)
    get_filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', get_filials)
    if st.button('Удалить филиал', key='del_filial_accept'):
        sql.Filials.delete_record(season_name=season_selector,
                                  filial_name=filial_selector)
        st.rerun()


@st.dialog('Переименовать филиал')
def rename_filial():
    seasons_df = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons_df)
    get_filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', get_filials)
    new_filial_name = st.text_input("Новое название филиала")
    if st.button('Переименовать', key='rename_season_accept'):
        sql.Filials.rename_filial(season_selector, filial_selector, new_filial_name)
        sql.Groups.rename_filial(season_selector, filial_selector, new_filial_name)
        sql.Records.rename_filial(season_selector, filial_selector, new_filial_name)
        st.rerun()


if st.button('Добавить филиал', key='add_filial', width=240):
    add_filial()

if st.button('Удалить филиал', key='del_filial', width=240):
    del_filial()

if st.button('Переименовать филиал', key='rename_filial', width=240):
    rename_filial()
