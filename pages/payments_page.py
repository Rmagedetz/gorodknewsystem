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


expenses = sql.Debits.get_df()
from_balance = sql.Payments_from_balance.get_df()

child_receipts = payments_df.groupby(['child_name'])['pay_sum'].sum().reset_index()
child_expenses = expenses.groupby(['child_name'])['pay_sum'].sum().reset_index()
child_from = from_balance.groupby(['child_name'])['pay_sum'].sum().reset_index()

children_list = pd.DataFrame(data=children, columns=['child_name'])
merged = children_list.merge(child_receipts, on='child_name', how='left')
merged = merged.merge(child_expenses, on='child_name', how='left')
merged = merged.merge(from_balance, on='child_name', how='left')

merged['pay_sum_x'] = merged['pay_sum_x'].fillna(0)
merged['pay_sum_y'] = merged['pay_sum_y'].fillna(0)
merged['pay_sum'] = merged['pay_sum'].fillna(0)

merged.rename(columns={"pay_sum_x": "child_receipts",
                       'pay_sum_y': 'child_expense',
                       'pay_sum': 'child_from'}, inplace=True)

merged['child_balance'] = merged['child_receipts'] - merged['child_expense'] - merged['child_from']

balances = merged[['child_name', 'child_balance']]


def get_child_balance(chld_name):
    """
    Возвращает баланс ребёнка по его ФИО.
    Если ребёнок не найден — возвращает 0.
    """
    row = balances[balances['child_name'] == chld_name]

    if not row.empty:
        return int(row['child_balance'].iloc[0])

    return 0


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
                                 "comment": "Комментарий",
                                 "season_name": "Сезон",
                                 "group_name": "Группа"
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

    child_balance = get_child_balance(child_selector)
    st.subheader(f'Баланс: {child_balance}')
    summa = st.text_input('Сумма')
    if child_balance > 0:
        from_balance_sum = st.number_input('Списать с баланса', min_value=0, max_value=child_balance)
    else:
        from_balance_sum = 0
    option_selector = st.selectbox('Тариф', options)
    comment = st.text_area('Комментарий', max_chars=100)
    if st.button('Добавить платеж', key='add_payment_accept'):
        if from_balance_sum > 0:
            sql.Payments_from_balance.add_object(
                datetime=datetime.datetime.now(),
                account=user,
                season_name=season_selector,
                group_name=group_selector,
                child_name=child_selector,
                parent_name=parents_selector,
                pay_form=pay_form_selector,
                pay_sum=from_balance_sum,
                option=option_selector,
                comment=comment
            )
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


@st.dialog("Редактирование платежа")
def edit_payment(payment_id, season, group, child, parent, form, summ, opt, comm):
    season_selector = st.selectbox('Сезон', list(seasons), key='season_selector',
                                   index=list(seasons).index(season))

    groups = sql.Groups.get_df(season_name=season)['group_name']
    group_selector = st.selectbox('Группа', list(groups), key='group_selector',
                                  index=list(groups).index(group))

    child_selector = st.selectbox('Ребенок', children,
                                  index=children.index(child))
    parents = sql.Records.get_parent_for_child(child_selector)
    parents_selector = st.selectbox('Родитель', parents,
                                    index=parent.index(parent))
    pay_form_selector = st.selectbox('Форма оплаты', list(pay_forms),
                                     index=list(pay_forms).index(form))
    summa = st.text_input('Сумма', value=summ)
    option_selector = st.selectbox('Тариф', list(options),
                                   index=list(options).index(opt))
    commnt = st.text_area('Комментарий', max_chars=100, value=comm)

    season_changed = season_selector != season
    group_changed = group_selector != group
    child_changed = child_selector != child
    parent_changed = parents_selector != parent
    form_changed = pay_form_selector != form
    summ_changed = float(summa) != float(summ)
    opt_changed = option_selector != opt
    comm_changed = commnt != comm

    something_changed = any([season_changed, group_changed, child_changed, parent_changed,
                             form_changed, summ_changed, opt_changed, comm_changed])

    if st.button('Изменить данные', key='edit_accept', disabled=not something_changed):
        sql.Payments.edit_record(payment_id,
                                 account=user,
                                 season_name=season_selector,
                                 group_name=group_selector,
                                 child_name=child_selector,
                                 parent_name=parents_selector,
                                 pay_form=pay_form_selector,
                                 pay_sum=summa,
                                 option=option_selector,
                                 comment=commnt + '_ред'
                                 )
        st.rerun()


if st.button("Добавить платеж", key="add_payment", width=150):
    add_payment()

if st.button('Удалить платеж', key='delete_payment', width=150):
    del_payment()

with st.expander('Редактировать платеж'):
    pay_id = st.selectbox('ID платежа', pay_ids)
    recent_data = payments_df[payments_df['id'] == pay_id]
    show = st.dataframe(recent_data,
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
                            "comment": "Комментарий",
                            "season_name": "Сезон",
                            "group_name": "Группа"
                        },
                        hide_index=True)

    data_to_func = recent_data.reset_index()
    season_name = data_to_func['season_name'][0]
    group_name = data_to_func['group_name'][0]
    child_name = data_to_func['child_name'][0]
    parent_name = data_to_func['parent_name'][0]
    pay_form = data_to_func['pay_form'][0]
    pay_sum = data_to_func['pay_sum'][0]
    option = data_to_func['option'][0]
    comment = data_to_func['comment'][0]

    if st.button('Редактировать платеж', key='edit_payment', width=150):
        edit_payment(pay_id, season_name, group_name, child_name, parent_name, pay_form, pay_sum, option, comment)
