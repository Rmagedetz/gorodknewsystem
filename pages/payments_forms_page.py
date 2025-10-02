import pandas as pd
import streamlit as st
import sql

permission = st.session_state.user_permissions['editing_groups'][0]

forms = sql.Payments_forms.get_df()

forms_df = st.dataframe(forms, column_config={'id': 'ID',
                                              'form': 'Форма оплаты'},
                        hide_index=True)


@st.dialog('Добавить форму оплаты')
def add_payment_form():
    form_name = st.text_input('Форма оплаты')
    if st.button('Добавить', key='add_payment_form_accept'):
        sql.Payments_forms.add_object(form=form_name)
        st.rerun()


@st.dialog('Удалить форму оплаты')
def del_payment_form():
    payment_forms = sql.Payments_forms.get_df()['form']
    selector = st.selectbox('Форма оплаты', payment_forms)
    if st.button('Удалить форму оплаты', key='del_payment_form_accept'):
        sql.Payments_forms.delete_record(form=selector)
        st.rerun()


if st.button('Добавить форму оплаты', key='add_payment_form', width=200):
    add_payment_form()

if st.button('Удалить форму оплаты', key='del_payment_form', width=200):
    del_payment_form()
