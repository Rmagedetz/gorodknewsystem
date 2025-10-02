import streamlit as st
import sql

children = sql.Child.get_df()

receipts = sql.Payments.get_df()
child_receipts = receipts.groupby(['child_name'])['pay_sum'].sum().reset_index()
parent_receipts = receipts.groupby(['parent_name'])['pay_sum'].sum().reset_index()

expenses = sql.Debits.get_df()
child_expenses = expenses.groupby(['child_name'])['pay_sum'].sum().reset_index()
parent_expenses = expenses.groupby(['parent_name'])['pay_sum'].sum().reset_index()

merged = children.merge(child_receipts, on='child_name', how='left')
merged = merged.merge(child_expenses, on='child_name', how='left')
merged['pay_sum_x'] = merged['pay_sum_x'].fillna(0)
merged['pay_sum_y'] = merged['pay_sum_y'].fillna(0)
merged['child_balance'] = merged['pay_sum_x'] - merged['pay_sum_y']
merged.rename(columns={"pay_sum_x": "child_receipts",
                       'pay_sum_y': 'child_expense'}, inplace=True)

merged = merged.merge(parent_receipts, on='parent_name', how='left')
merged = merged.merge(parent_expenses, on='parent_name', how='left')
merged['pay_sum_x'] = merged['pay_sum_x'].fillna(0)
merged['pay_sum_y'] = merged['pay_sum_y'].fillna(0)
merged['parent_balance'] = merged['pay_sum_x'] - merged['pay_sum_y']
merged.rename(columns={"pay_sum_x": "parent_receipts",
                       'pay_sum_y': 'parent_expense'}, inplace=True)

column_config = {'child_name': 'ФИО Ребенка',
                 'parent_name': 'ФИО Родителя',
                 'child_age': 'Возраст',
                 'child_birthday': 'ДР',
                 'parent_add': 'Доп контакт',
                 'phone_add': 'Доп номер',
                 'leave': 'Уходит сам',
                 'additional_contact': 'Доп контакт',
                 'addr': 'Адрес',
                 'disease': 'Заболевания',
                 'allergy': 'Аллергии',
                 'other': 'Другое',
                 'physic': 'Ограничения',
                 'swimm': 'Бассейн',
                 'jacket_swimm': 'Жилет',
                 'hobby': 'Хобби',
                 'school': 'Школа',
                 'additional_info': 'Доп информация',
                 'departures': '',
                 'referer': 'Откуда узнали',
                 'ok': '',
                 'mailing': 'Рассылка',
                 'personal_accept': 'Согалсие',
                 'oms': 'ОМС',
                 'child_balance': 'Баланс ребенка',
                 'parent_balance': 'Баланс родителя'}

sh = st.dataframe(merged, column_config=column_config,
                  hide_index=True)
show = st.dataframe(merged[['child_name', 'child_balance',
                            'parent_name', 'parent_balance']],
                    column_config=column_config)
