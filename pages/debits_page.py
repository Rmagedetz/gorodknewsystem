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
children = sql.Records.get_all_unique_children()
pay_forms = sql.Payments_forms.get_df()['form']

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


@st.dialog('Редактирование списания')
def edit_debit(id, season, filial, group, child, parent, form, summ, opt, comm):
    season_selector = st.selectbox('Сезон', list(seasons), key='season_selector',
                                   index=list(seasons).index(season))

    filials = sql.Filials.get_df(season_name=season_selector)['filial_name']
    filial_selector = st.selectbox('Филиал', list(filials),
                                   index=list(filials).index(filial))
    groups = sql.Groups.get_df(season_name=season)['group_name']
    group_selector = st.selectbox('Группа', list(groups), key='group_selector',
                                  index=list(groups).index(group))

    child_selector = st.selectbox('Ребенок', children,
                                  index=children.index(child))
    parents = sql.Records.get_parent_for_child(child_selector)
    parents_selector = st.selectbox('Родитель', parents,
                                    index=parent.index(parent))
    summa = st.text_input('Сумма', value=summ)
    option_selector = st.selectbox('Форма оплаты', list(pay_forms),
                                   index=list(pay_forms).index(form))

    selector_list = ['Путевка', 'Доп.время', 'Возврат', 'Мерч']
    pay_option_selector = st.selectbox('Тип оплаты',
                                       selector_list,
                                       index=selector_list.index(opt))
    commnt = st.text_area('Комментарий', max_chars=100, value=comm)

    season_changed = season_selector != season
    filial_changed = filial_selector != filial
    group_changed = group_selector != group
    child_changed = child_selector != child
    parent_changed = parents_selector != parent
    form_changed = option_selector != form
    pay_opt_changed = pay_option_selector != opt
    summ_changed = float(summa) != float(summ)
    opt_changed = option_selector != opt
    comm_changed = commnt != comm

    something_changed = any([season_changed, filial_changed, group_changed, child_changed, parent_changed,
                             form_changed, pay_opt_changed, summ_changed, opt_changed, comm_changed])

    if st.button('Изменить данные', key='edit_accept', disabled=not something_changed):
        sql.Debits.edit_record(id,
                               account=user,
                               season_name=season_selector,
                               filial_name=filial_selector,
                               group_name=group_selector,
                               child_name=child_selector,
                               parent_name=parents_selector,
                               pay_sum=summa,
                               pay_form=option_selector,
                               option=pay_option_selector,
                               comment=commnt + '_ред'
                               )
        st.rerun()


if st.button('Добавить списание', key="add_debit", width=170):
    add_debit()

if st.button('Удалить списание', key='delete_debit', width=170):
    del_debit()

with st.expander('Редактировать списание'):
    debit_id = st.selectbox('ID списания', debits_ids)
    recent_data = debits_df[debits_df['id'] == debit_id]
    show = st.dataframe(recent_data,
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

    data_to_func = recent_data.reset_index()
    season_name = data_to_func['season_name'][0]
    filial_name = data_to_func['filial_name'][0]
    group_name = data_to_func['group_name'][0]
    child_name = data_to_func['child_name'][0]
    parent_name = data_to_func['parent_name'][0]
    pay_form = data_to_func['pay_form'][0]
    pay_sum = data_to_func['pay_sum'][0]
    option = data_to_func['option'][0]
    comment = data_to_func['comment'][0]

    if st.button('Редактировать списание', key='edit_payment', width=150):
        edit_debit(debit_id,
                   season_name, filial_name, group_name, child_name, parent_name, pay_form, pay_sum, option, comment)
