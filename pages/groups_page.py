import streamlit as st
import sql

groups_df = sql.Groups.get_df()
permission = st.session_state.user_permissions['editing_groups'][0]

st.dataframe(groups_df, column_config={
    'group_id': st.column_config.Column('ID'),
    'season_name': st.column_config.Column('Название сезона'),
    'filial_name': st.column_config.Column('Название филиала'),
    'group_name': st.column_config.Column('Название группы'),
    'start_date': st.column_config.DateColumn('Дата начала', format='DD.MM.YYYY'),
    'end_date': st.column_config.DateColumn('Дата окончания', format='DD.MM.YYYY'),
    'capacity': st.column_config.Column('Вместимость'),
    'days': st.column_config.Column('Дн.')
}, hide_index=True)


@st.dialog("Добавление группы")
def add_group():
    seasons = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons)
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials)
    group_name = st.text_input('Название группы')
    start_date = st.date_input('Дата начала', format='DD.MM.YYYY')
    end_date = st.date_input('Дата окончания', format='DD.MM.YYYY')
    days = (end_date - start_date).days
    capacity = st.number_input('Вместимость', min_value=0)
    if st.button("Добавить группу", key='add_group_accept'):
        sql.Groups.add_record(
            season_name=season_selector,
            filial_name=filial_selector,
            group_name=group_name,
            start_date=start_date,
            end_date=end_date,
            capacity=capacity,
            days=days
        )
        st.rerun()


@st.dialog("Удаление группы")
def del_group():
    seasons = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons)
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials)
    groups = sql.Groups.get_df(season_name=season_selector,
                               filial_name=filial_selector)['group_name']
    groups_selector = st.selectbox('Название группы', groups)

    if st.button("Удалить группу", key='del_group_accept'):
        sql.Groups.delete_record(
            season_name=season_selector,
            filial_name=filial_selector,
            group_name=groups_selector
        )
        st.rerun()


@st.dialog('Редактирование группы')
def edit_group():
    seasons = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons)
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials)
    groups = sql.Groups.get_df(season_name=season_selector,
                               filial_name=filial_selector)['group_name']
    groups_selector = st.selectbox('Название группы', groups)
    if season_selector and filial_selector and groups_selector:
        data = sql.Groups.get_df(season_name=season_selector,
                                 filial_name=filial_selector,
                                 group_name=groups_selector).reset_index()
        start_date = st.date_input('Дата начала',
                                   format='DD.MM.YYYY',
                                   value=data['start_date'][0])
        end_date = st.date_input('Дата окончания',
                                 format='DD.MM.YYYY',
                                 value=data['end_date'][0])
        capacity = st.number_input('Вместимость',
                                   value=data['capacity'][0])
        if st.button('Редактировать группу', key='edit_group_accept'):
            sql.Groups.edit_record(season_selector, filial_selector, groups_selector,
                                   start_date=start_date,
                                   end_date=end_date,
                                   capacity=capacity)
            st.rerun()


@st.dialog('Переименование группы')
def rename_group():
    seasons = sql.Seasons.get_df()['season_name']
    season_selector = st.selectbox('Сезон', seasons)
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials)
    groups = sql.Groups.get_df(season_name=season_selector,
                               filial_name=filial_selector)['group_name']
    groups_selector = st.selectbox('Название группы', groups)
    new_group_name = st.text_input('Новое название группы')
    if st.button('Переименовать группу', key='rename_group_accept'):
        sql.Groups.rename_group(season_selector, filial_selector, groups_selector, new_group_name)
        sql.Records.rename_group(season_selector, filial_selector, groups_selector, new_group_name)
        st.rerun()


if st.button('Добавить группу', key='add_group', width=240):
    add_group()

if st.button('Удалить группу', key='del_group', width=240):
    del_group()

if st.button('Редактировать группу', key='edit_group', width=240):
    edit_group()

if st.button('Переименовать группу', key='rename_group', width=240):
    rename_group()
