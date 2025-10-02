import pandas as pd
import streamlit as st
import sql

permission = st.session_state.user_permissions['editing_groups'][0]

forms = sql.Payment_options.get_df()

forms_df = st.dataframe(forms, column_config={'id': 'ID',
                                              'option': 'Тариф'},
                        hide_index=True)


@st.dialog('Добавить тариф')
def add_payment_option():
    option_name = st.text_input('Тариф')
    if st.button('Добавить', key='add_payment_option_accept'):
        sql.Payment_options.add_object(option=option_name)
        st.rerun()


@st.dialog('Удалить тариф')
def del_payment_option():
    payment_options = sql.Payment_options.get_df()['option']
    selector = st.selectbox('Тариф', payment_options)
    if st.button('Удалить тариф', key='del_payment_option_accept'):
        sql.Payment_options.delete_record(option=selector)
        st.rerun()


if st.button('Добавить тариф', key='add_option_form', width=200):
    add_payment_option()

if st.button('Удалить тариф', key='del_option_form', width=200):
    del_payment_option()
