import datetime

import pandas as pd
import streamlit as st
import sql

permission = st.session_state.user_permissions['editing_groups'][0]
user = st.session_state.user

payments_df = sql.Payments.get_df()
children = sql.Records.get_all_unique_children()
pay_forms = sql.Payments_forms.get_df()['form']
options = sql.Payment_options.get_df()['option']
pay_ids = payments_df['id']
seasons = sql.Seasons.get_df()['season_name']

payments_show = st.dataframe(payments_df,
                             column_config={
                                 "id": "ID",
                                 "datetime": st.column_config.DatetimeColumn('Время',
                                                                             format='DD.MM.YY - HH:mm'),
                                 "account": "Кто провел",
                                 "child_name": "ФИО Ребенка",
                                 "parent_name": "ФИО Родителя",
                                 "pay_form": "Форма оплаты",
                                 "pay_sum": "Сумма",
                                 "option": "Тариф",
                                 "comment": "Комментарий"
                             },
                             hide_index=True)


@st.dialog("Добавление платежа")
def add_payment():
    season_selector = st.selectbox('Сезон', seasons, key='season_selector')
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials, key='filial_selector')
    groups = sql.Groups.get_df(season_name=season_selector, filial_name=filial_selector)['group_name']
    group_selector = st.selectbox('Группа', groups, key='group_selector')
    child_selector = st.selectbox('Ребенок', children)
    parents = sql.Records.get_parent_for_child(child_selector)
    parents_selector = st.selectbox('Родитель', parents)
    pay_form_selector = st.selectbox('Форма оплаты', pay_forms)
    summa = st.text_input('Сумма')
    option_selector = st.selectbox('Тариф', options)
    comment = st.text_area('Комментарий', max_chars=100)
    if st.button('Добавить платеж', key='add_payment_accept'):
        sql.Payments.add_object(
            datetime=datetime.datetime.now(),
            account=user,
            season_name=season_selector,
            group_name=group_selector,
            child_name=child_selector,
            parent_name=parents_selector,
            pay_form=pay_form_selector,
            pay_sum=summa,
            option=option_selector,
            comment=comment
        )
        sql.Records.update_record_status(
            season_name=season_selector,
            filial_name=filial_selector,
            group_name=group_selector,
            parent_name=parents_selector,
            child_name=child_selector
        )
        st.rerun()


@st.dialog("Удаление платежа")
def del_payment():
    pay_id = st.selectbox('ID платежа', pay_ids)
    show = payments_df[payments_df['id'] == pay_id].T
    st.write(show)
    if st.button('Удалить платеж', key='delete_payment_accept'):
        sql.Payments.delete_record(id=pay_id)
        st.rerun()


if st.button("Добавить платеж", key="add_payment", width=150):
    add_payment()

if st.button('Удалить платеж', key='delete_payment', width=150):
    del_payment()
