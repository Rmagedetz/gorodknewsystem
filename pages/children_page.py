import streamlit as st
import sql
import pandas as pd

# --- 1. Список всех детей ---
children = sql.Child.get_df()

column_config_children = {
    'child_name': 'ФИО Ребенка',
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
    'oms': 'ОМС'
}

st.dataframe(children, column_config=column_config_children, hide_index=True)

# --- 2. Балансы с учётом списаний и списаний с баланса ---
# Получаем все платежи и расходы
receipts = sql.Payments.get_df()
from_balance = sql.Payments_from_balance.get_df()
expenses = sql.Debits.get_df()


# Функция для расчёта баланса
def calculate_balance(df, key_col):
    return df.groupby(key_col)['pay_sum'].sum().reset_index()


# Агрегации
child_receipts = calculate_balance(receipts, 'child_name')
child_expenses = calculate_balance(expenses, 'child_name')
child_from_balance = calculate_balance(from_balance, 'child_name')

parent_receipts = calculate_balance(receipts, 'parent_name')
parent_expenses = calculate_balance(expenses, 'parent_name')
parent_from_balance = calculate_balance(from_balance, 'parent_name')

# --- Merge для детей ---
merged = children.merge(child_receipts, on='child_name', how='left') \
    .merge(child_expenses, on='child_name', how='left', suffixes=('', '_expense')) \
    .merge(child_from_balance, on='child_name', how='left', suffixes=('', '_from_balance'))

for col in ['pay_sum', 'pay_sum_expense', 'pay_sum_from_balance']:
    merged[col] = merged[col].fillna(0)

merged['child_balance'] = merged['pay_sum'] - merged['pay_sum_expense'] - merged['pay_sum_from_balance']
merged.rename(columns={
    'pay_sum': 'child_receipts',
    'pay_sum_expense': 'child_expense',
    'pay_sum_from_balance': 'child_from_balance'
}, inplace=True)

# --- Merge для родителей ---
merged = merged.merge(parent_receipts, on='parent_name', how='left') \
    .merge(parent_expenses, on='parent_name', how='left', suffixes=('', '_expense')) \
    .merge(parent_from_balance, on='parent_name', how='left', suffixes=('', '_from_balance'))

for col in ['pay_sum', 'pay_sum_expense', 'pay_sum_from_balance']:
    merged[col] = merged[col].fillna(0)

merged['parent_balance'] = merged['pay_sum'] - merged['pay_sum_expense'] - merged['pay_sum_from_balance']
merged.rename(columns={
    'pay_sum': 'parent_receipts',
    'pay_sum_expense': 'parent_expense',
    'pay_sum_from_balance': 'parent_from_balance'
}, inplace=True)

# --- Сортировка ---
merged['zero_group'] = (merged['child_balance'] == 0) & (merged['parent_balance'] == 0)
merged = merged.sort_values(by=['zero_group', 'child_name', 'parent_name'],
                            ascending=[True, True, True])

# --- Краткий DataFrame для вывода балансов ---
balance_df = merged[['child_name', 'child_balance', 'parent_name', 'parent_balance']].copy()


# --- Подсветка балансов ---
def highlight_balances(row):
    return [
        "background-color: #ffb3b3" if col < 0 else
        "background-color: #e6e6e6" if col == 0 else
        "background-color: #b3ffb3" if col > 0 else ""
        for col, name in zip(row, row.index)
        if name in ['child_balance', 'parent_balance']
    ] + [""] * (len(row) - 2)  # остальные колонки без стиля


styled_balance_df = balance_df.style.apply(highlight_balances, axis=1)

column_config_balance = {
    'child_name': 'ФИО Ребенка',
    'child_balance': 'Баланс ребенка',
    'parent_name': 'ФИО Родителя',
    'parent_balance': 'Баланс родителя'
}

st.dataframe(styled_balance_df, column_config=column_config_balance, width='content')