import streamlit as st
import sql

seasons_df = sql.Seasons.get_df()
permission = st.session_state.user_permissions['editing_seasons'][0]

st.dataframe(seasons_df, column_config={
    'season_id': st.column_config.Column('ID'),
    'season_name': st.column_config.Column('Название сезона'),
    'start_date': st.column_config.DateColumn('Дата начала', format='DD.MM.YYYY'),
    'end_date': st.column_config.DateColumn('Дата окончания', format='DD.MM.YYYY')
}, hide_index=True)


@st.dialog('Добавление сезона')
def add_season():
    season_name = st.text_input('Название сезона')
    start_date = st.date_input('Дата начала', format='DD.MM.YYYY')
    end_date = st.date_input('Дата окончания', format='DD.MM.YYYY')
    if st.button('Добавить', key='add_season_accept'):
        sql.Seasons.add_record(season_name=season_name,
                               start_date=start_date,
                               end_date=end_date)
        st.rerun()


@st.dialog('Удаление сезона')
def del_season():
    seasons_list = list(seasons_df['season_name'])
    season_selector = st.selectbox('Название сезона', seasons_list)
    if st.button('Удалить', key='del_season_accept'):
        sql.Seasons.delete_record(season_name=season_selector)
        st.rerun()


@st.dialog('Редактирование сезона')
def edit_season():
    seasons_list = list(seasons_df['season_name'])
    season_selector = st.selectbox('Название сезона', seasons_list)
    data = seasons_df[seasons_df['season_name'] == season_selector].reset_index()
    start_date = st.date_input('Дата начала',
                               format='DD.MM.YYYY',
                               value=data['start_date'][0])
    end_date = st.date_input('Дата окончания',
                             format='DD.MM.YYYY',
                             value=data['end_date'][0])
    if st.button('Редактировать', key='edit_season_accept'):
        sql.Seasons.edit_record(season_selector,
                                start_date=start_date,
                                end_date=end_date)
        st.rerun()


@st.dialog('Переименование сезона')
def rename_season():
    seasons_list = list(seasons_df['season_name'])
    season_selector = st.selectbox('Название сезона', seasons_list)
    new_season_name = st.text_input('Новое название сезона')
    if st.button('Переименовать', key='rename_season_accept'):
        sql.Seasons.edit_record(season_selector,
                                season_name=new_season_name)
        sql.Filials.rename_season(season_selector, new_season_name)
        sql.Groups.rename_season(season_selector, new_season_name)
        st.rerun()


if st.button('Добавить сезон', key='add_season', width=240):
    add_season()

if st.button('Удалить сезон', key='del_season', width=240):
    del_season()

if st.button('Редактировать сезон', key='edit_season', width=240):
    edit_season()

if st.button('Переименовать сезон', key='rename_season', width=240):
    rename_season()
