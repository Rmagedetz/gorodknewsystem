import streamlit as st
import sql


# -------------------------------
# Настройка Streamlit (твой код остаётся без изменений)
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.set_page_config(
    page_title="Записи и группы Городок",
    layout="wide",
    page_icon="logo.png"
)


def login():
    with st.form("login_form", clear_on_submit=True):
        st.title("Вход в приложение")
        user_input = st.text_input("Введите логин")
        password_input = st.text_input("Введите пароль", type="password")
        submit = st.form_submit_button("Войти")

        if submit:
            if user_input in sql.User.get_user_list_for_login():
                if password_input == sql.User.check_user_password(user_input):
                    user_permissions = sql.User.get_df(user_name=user_input).reset_index()
                    st.session_state.user_permissions = user_permissions
                    st.session_state.logged_in = True
                    st.session_state.user = user_input
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            else:
                st.error("Неверный логин или пароль")


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Выйти", icon=":material/logout:")
users_page = st.Page("pages/users_page.py", title="Пользователи", icon=":material/groups_2:")
seasons_page = st.Page("pages/seasons_page.py", title="Сезоны", icon=":material/calendar_month:")
filials_page = st.Page("pages/filials_page.py", title="Филиалы", icon=":material/apartment:")
groups_page = st.Page("pages/groups_page.py", title="Группы", icon=":material/group:")

records_page = st.Page("pages/records_page.py", title="Записи", icon=":material/table_view:", default=True)
group_card_page = st.Page("pages/group_card_page.py", title="Вкладки групп", icon=":material/group:")

child_page = st.Page("pages/children_page.py", title="Дети",
                     icon=":material/child_hat:")
parents_page = st.Page("pages/parents_page.py", title="Родители",
                       icon=":material/account_child_invert:")

ankets_page = st.Page("pages/ankets_page.py", title="Анкеты",
                      icon=":material/frame_person:")
ankets_viewer_page = st.Page('pages/ankets_viewer_page.py', title='Просмотрщик анкет',
                             icon=":material/recent_actors:")

payments_forms_page = st.Page("pages/payments_forms_page.py", title="Формы оплаты",
                              icon=":material/credit_card_gear:")
payments_options_page = st.Page("pages/payment_options_page.py", title="Тарифы",
                                icon=":material/family_history:")
payments_page = st.Page("pages/payments_page.py", title="Платежи",
                        icon=":material/currency_ruble:")
debits_page = st.Page("pages/debits_page.py", title="Списания",
                      icon=":material/payment_arrow_down:")
bot_page = st.Page('pages/bot_page.py', title='Рассылка в боте',
                   icon=":material/smart_toy:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "🔏 Администрирование": [logout_page, users_page, seasons_page, filials_page, groups_page],
            "📚 Записи и группы": [records_page, group_card_page],
            "💳 Платежи и списания": [payments_forms_page, payments_options_page, payments_page, debits_page],
            "👨‍👨‍👦 Дети и родители": [child_page, parents_page],
            "📒 Анкеты": [ankets_page, ankets_viewer_page],
            "🤖 Бот": [bot_page]
        }
    )
    big_logo = "logo_2.png"
    small_logo = "logo.png"
    st.logo(big_logo, size="large", icon_image=small_logo)
else:
    pg = st.navigation([login_page])

pg.run()
