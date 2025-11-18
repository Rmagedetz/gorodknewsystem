import streamlit as st
import sql
import telebot
import time
import random

BOT2_TOKEN = "8534605207:AAFm58K368UwZYdZ2MFJ87BxZQHUz2OwXwA"
bot2 = telebot.TeleBot(BOT2_TOKEN)

bot_users_data = sql.Bot_subscribers.get_df()
bot_users_data['check'] = False

cols = ['check'] + [col for col in bot_users_data.columns if col != 'check']
bot_users_data = bot_users_data[cols]

column_labels = {
    'check': 'Выбор',
    'id': 'ID',
    'datetime': 'Дата регистрации',
    'subscriber_tg_id': 'TG ID',
    'subscriber_tg_first_name': 'Имя TG',
    'subscriber_tg_last_name': 'Фамилия TG',
    'subscriber_tg_username': 'Никнейм TG',
    'present_accepted': 'Подарок получен',
    'subscriber_real_first_name': 'Настоящее имя',
    'subscriber_real_last_name': 'Настоящая фамилия',
    'subscriber_real_username': 'Настоящий никнейм',
    'subscriber_child_name': 'Имя ребёнка',
    'subscriber_child_birthday': 'ДР ребёнка',
}

# Настройки ширины — узкие колонки
column_config = {}

for col in bot_users_data.columns:
    if col == 'check':
        column_config[col] = st.column_config.CheckboxColumn(
            column_labels[col],
            width="small"
        )
    else:
        column_config[col] = st.column_config.TextColumn(
            column_labels.get(col, col),
            width="small",
            disabled=True     # 🔒 запрещаем редактирование
        )
column_config['present_accepted'] = st.column_config.CheckboxColumn('Подарок',
                                                                    disabled=True, help='Подарок получен', width='small')

column_config['check'] = st.column_config.CheckboxColumn('Добавить', help='Добавить в рассылку', width='small')

edited_df = st.data_editor(
    bot_users_data,
    column_config=column_config,
    hide_index=True,
)

message_text = st.text_area(
    "Введите текст сообщения:",
    max_chars=3500,
    height=200,
    placeholder="Введите текст, который хотите отправить выбранным пользователям… (макс. 3500 символов)"
)

if st.button("Отправить сообщение выбранным пользователям"):
    # Фильтрация выбранных
    selected_users = edited_df[edited_df['check'] == True]

    if selected_users.empty:
        st.warning("Не выбран ни один пользователь.")
    elif not message_text.strip():
        st.warning("Нельзя отправить пустое сообщение.")
    else:
        st.success(f"Начинаем рассылку. Пользователей: {len(selected_users)}")

        progress = st.progress(0)
        status = st.empty()

        total = len(selected_users)
        for i, (_, row) in enumerate(selected_users.iterrows(), start=1):
            tg_id = row['subscriber_tg_id']

            try:
                bot2.send_message(tg_id, message_text)
            except Exception as e:
                status.write(f"Ошибка отправки пользователю {tg_id}: {e}")

            progress.progress(i / total)
            status.write(f"Отправлено {i} из {total}")

            time.sleep(random.randint(1, 5))  # Рандомная пауза

        status.write("✔ Рассылка завершена!")
        st.balloons()