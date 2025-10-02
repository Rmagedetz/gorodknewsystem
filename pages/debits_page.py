import datetime

import pandas as pd
import streamlit as st
import sql
from decimal import Decimal

permission = st.session_state.user_permissions['editing_groups'][0]
user = st.session_state.user

debits_df = sql.Debits.get_df()
receipts = sql.Payments.get_df()
debits_ids = debits_df['id']
seasons = sql.Seasons.get_df()['season_name']

show = st.dataframe(debits_df,
                    column_config={
                        "id": "ID",
                        "datetime": st.column_config.DatetimeColumn('Время',
                                                                    format='DD.MM.YY - HH:mm'),
                        "account": "Кто провел",
                        'season_name': 'Сезон',
                        'filial_name': 'Филиал',
                        'group_name': "Группа",
                        "child_name": "ФИО Ребенка",
                        "parent_name": "ФИО Родителя",
                        "pay_form": "Форма оплаты",
                        "pay_sum": "Сумма",
                        "option": "Тип оплаты",
                        "comment": "Комментарий"
                    },
                    hide_index=True)


@st.dialog("Добавить списание")
def add_debit():
    season_selector = st.selectbox('Сезон', seasons)
    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', filials)
    groups = sql.Groups.get_df(season_name=season_selector,
                               filial_name=filial_selector)['group_name']
    groups_selector = st.selectbox('Группа', groups)
    children = sql.Records.get_all_unique_children(season_name=season_selector)
    child_selector = st.selectbox('Ребенок', children)
    parents = sql.Records.get_parent_for_child(child_selector, season_name=season_selector)
    parent_selector = st.selectbox('Родитель', parents)
    pay_option_selector = st.selectbox('Тип оплаты',
                                       ['Путевка', 'Доп.время', 'Возврат', 'Мерч'])
    pay_forms = receipts[
        (receipts['child_name'] == child_selector) &
        (receipts['parent_name'] == parent_selector)
        ]['pay_form'].unique()
    if len(pay_forms) == 0:
        st.write("Списывать нечего. Оплата за этого ребенка не вносилась")
    else:
        pay_form_selector = st.selectbox('Форма оплаты', pay_forms)
        receipts_total = receipts[receipts['child_name'] == child_selector]['pay_sum'].sum()
        expenses_total = debits_df[debits_df['child_name'] == child_selector]['pay_sum'].sum()
        balance = receipts_total - expenses_total
        st.write(f'Текущий баланс по ребенку: {balance}')
        summa = st.text_input('Сумма')
        if summa and Decimal(summa) > balance:
            st.write("Списание данной суммы приведет к отрицательному балансу по ребенку")
        comment = st.text_area('Комментарий', max_chars=100)
        if st.button('Добавить списание', key='add_debit_accept'):
            sql.Debits.add_object(
                datetime=datetime.datetime.now(),
                account=user,
                season_name=season_selector,
                filial_name=filial_selector,
                group_name=groups_selector,
                child_name=child_selector,
                parent_name=parent_selector,
                pay_sum=summa,
                pay_form=pay_form_selector,
                option=pay_option_selector,
                comment=comment
            )
            st.rerun()


@st.dialog("Удаление списания")
def del_debit():
    debit_id = st.selectbox('ID списания', debits_ids)
    show = debits_df[debits_df['id'] == debit_id].T
    st.write(show)
    if st.button('Удалить списание', key='delete_debit_accept'):
        sql.Debits.delete_record(id=debit_id)
        st.rerun()


if st.button('Добавить списание', key="add_debit", width=170):
    add_debit()

if st.button('Удалить списание', key='delete_debit', width=170):
    del_debit()
