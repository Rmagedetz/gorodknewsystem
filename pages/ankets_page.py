import pandas as pd
import streamlit as st
import sql
from gtables_functions import get_quiz_data

permission = st.session_state.user_permissions['editing_groups'][0]

ankets_df = sql.Ankets.get_df()

column_config = {'name': 'ФИО Ребенка',
                 'parent_main_name': 'ФИО Родителя',
                 'parent_main_phone':'Тел',
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

show = st.dataframe(ankets_df, column_config=column_config, hide_index=True)

if st.button('Подгрузить данные из гугл-таблицы', width=300, key='load_ankets_from_gt'):
    st.toast('Подключаемся к гугл-таблице')
    quiz_data_raw = get_quiz_data()
    st.toast('Преобразуем данные')
    df = pd.DataFrame(quiz_data_raw)
    st.toast('Конвертируем даты')
    df["child_birthday"] = pd.to_datetime(
        df["child_birthday"], format="%d.%m.%Y", errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Если даты некорректные, они станут NaT -> можно заменить на None
    df = df.where(pd.notnull(df), None)

    # Преобразуем DataFrame в список словарей для batch_add
    records = df.to_dict(orient="records")
    st.toast('Загружаем данные в базу')
    sql.Ankets.batch_add(records)
    st.success("Данные успешно сохранены!")


@st.dialog("Привязка анкеты к ребенку")
def attach_anket_to_child():
    parents = sql.Records.get_unique_parents()
    parent_selector = st.selectbox('Родитель', parents)
    children = sql.Records.get_children_for_parent(parent_selector)
    child_selector = st.selectbox('Ребенок', children)
    anket_selector = st.selectbox('Анкета', ankets_df['name'])
    anket_data = ankets_df[ankets_df['name'] == anket_selector].reset_index()
    if st.button('Привязать анкету', key='attach_anket_to_child_accept'):
        sql.Records.rename_child(parent_selector, child_selector, anket_selector)
        sql.Child.attach_anket_to_child(child_selector, parent_selector, anket_data)
        st.rerun()


@st.dialog("Привязка анкеты к родителю")
def attach_anket_to_parent():
    children = sql.Records.get_all_unique_children()
    children_selector = st.selectbox('Ребенок', children)
    parents = sql.Records.get_parent_for_child(children_selector)
    parent_selector = st.selectbox('Родитель', parents)
    anket_selector = st.selectbox('Анкета', ankets_df['parent_main_name'])
    anket_data = ankets_df[ankets_df['parent_main_name'] == anket_selector].reset_index()
    st.write(anket_data)
    if st.button('Привязать анкету', key='attach_anket_to_child_accept'):
        sql.Records.rename_parent(children_selector, parent_selector, anket_selector)
        sql.Child.rename_parent(children_selector, parent_selector, anket_selector)
        sql.Parent.attach_anket_to_parent(parent_selector, anket_data)
        st.rerun()


if st.button('Привязать анкету к ребенку', width=300, key='attach_anket_to_child'):
    attach_anket_to_child()

if st.button('Привязать анкету к родителю', width=300, key='attach_anket_to_parent'):
    attach_anket_to_parent()
