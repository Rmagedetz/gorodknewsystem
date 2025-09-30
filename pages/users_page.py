import streamlit as st
import sql

users_df = sql.User.get_df()
if st.session_state.user_permissions['editing_users'][0]:
    st.dataframe(users_df, column_config={
        'user_id': st.column_config.Column('ID Пользователя'),
        'user_name': st.column_config.Column('Имя пользователя'),
        'password': st.column_config.Column('Пароль'),
        'editing_users': st.column_config.CheckboxColumn('Пользователи', help='Может редактировать пользователей'),
        'editing_seasons': st.column_config.CheckboxColumn('Сезоны', help='Может редактировать сезоны'),
        'editing_filials': st.column_config.CheckboxColumn('Филиалы', help='Может редактировать филиалы'),
        'editing_groups': st.column_config.CheckboxColumn('Группы', help='Может редактировать группы'),
        'editing_records': st.column_config.CheckboxColumn('Записи', help='Может редактировать записи'),
        'editing_payments': st.column_config.CheckboxColumn('Платежи', help='Может редактировать платежи'),
        'editing_visits': st.column_config.CheckboxColumn('Посещаемость', help='Может редактировать посещения')
    }, hide_index=True)


    @st.dialog('Добавление пользователя')
    def add_user():
        user_name = st.text_input('Имя пользователя')
        password = st.text_input('Пароль', type='password')
        password_accept = st.text_input('Подтверждение пароля', type='password')

        with st.container(border=True):
            st.write('Права пользователя')
            editing_users = st.checkbox('Редактирование пользователей')
            editing_seasons = st.checkbox('Редактирование сезонов')
            editing_filials = st.checkbox('Редактирование филиалов')
            editing_groups = st.checkbox('Редактирование групп')
            editing_records = st.checkbox('Редактирование записей')
            editing_payments = st.checkbox('Редактирование платежей')
            editing_visits = st.checkbox('Редактирование посещаемости')

        if st.button('Добавить', key='add_user_acceptation'):
            if password != password_accept:
                st.error('Пароли не совпадают')
            else:
                if user_name in list(users_df['user_name']):
                    st.error('Пользователь с таким именем уже существует')
                else:
                    sql.User.add_record(
                        user_name=user_name,
                        password=password,
                        editing_users=editing_users,
                        editing_seasons=editing_seasons,
                        editing_filials=editing_filials,
                        editing_groups=editing_groups,
                        editing_records=editing_records,
                        editing_payments=editing_payments,
                        editing_visits=editing_visits
                    )
                    st.rerun()


    @st.dialog('Удаление пользователя')
    def delete_user():
        user_list = list(users_df['user_name'])
        user_list.remove(st.session_state.user)
        user_selection = st.selectbox('Пользователь', user_list)
        if st.button('Удалить пользователя', key='del_user_accept'):
            sql.User.delete_record(user_name=user_selection)
            st.rerun()


    @st.dialog('Редактирование пользователя')
    def edit_user():
        user_list = list(users_df['user_name'])
        user_selection = st.selectbox('Пользователь', user_list)
        user_permissions = sql.User.get_df(user_name=user_selection).reset_index()
        new_password = st.text_input('Новый пароль',
                                     value=user_permissions['password'][0],
                                     type='password',
                                     key='new_password')
        new_password_accept = st.text_input('Новый пароль',
                                            value=user_permissions['password'][0],
                                            type='password',
                                            key='new_password_accept')
        with st.container(border=True):
            editing_users = st.checkbox('Редактирование пользователей',
                                        value=user_permissions['editing_users'][0])
            editing_seasons = st.checkbox('Редактирование сезонов',
                                          value=user_permissions['editing_seasons'][0])
            editing_filials = st.checkbox('Редактирование филиалов',
                                          value=user_permissions['editing_filials'][0])
            editing_groups = st.checkbox('Редактирование групп',
                                         value=user_permissions['editing_groups'][0])
            editing_records = st.checkbox('Редактирование записей',
                                          value=user_permissions['editing_records'][0])
            editing_payments = st.checkbox('Редактирование платежей',
                                           value=user_permissions['editing_payments'][0])
            editing_visits = st.checkbox('Редактирование посещаемости',
                                         value=user_permissions['editing_visits'][0])
        if st.button('Редактировать', key='edit_user_accept'):
            if new_password != new_password_accept:
                st.error("Пароли не совпадают")
            else:
                sql.User.edit_record(name=user_selection,
                                     password=new_password,
                                     editing_users=editing_users,
                                     editing_seasons=editing_seasons,
                                     editing_filials=editing_filials,
                                     editing_groups=editing_groups,
                                     editing_records=editing_records,
                                     editing_payments=editing_payments,
                                     editing_visits=editing_visits
                                     )
                st.rerun()


    if st.button('Добавить пользователя', key='add_user_btn', width=240):
        add_user()
    if st.button('Удалить пользователя', key='delete_user_btn', width=240):
        delete_user()
    if st.button('Редактировать пользователя', key='edit_user', width=240):
        edit_user()
else:
    st.write('Функция редактирования пользователей недоступна')
