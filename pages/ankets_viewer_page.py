import pandas as pd
import streamlit as st
import sql

from io import BytesIO
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.pagebreak import Break
import copy

permission = st.session_state.user_permissions['editing_groups'][0]

ankets_df = sql.Ankets.get_df()

column_config = {'name': 'ФИО Ребенка',
                 'parent_main_name': 'ФИО Родителя',
                 'parent_main_phone': 'Тел',
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

child_selector = st.selectbox('Ребенок', options=ankets_df['name'])

data = ankets_df[ankets_df['name'] == child_selector].reset_index()

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True, height=600):
        st.subheader('🧒 Данные ребенка')
        st.divider()
        st.write(f'ФИО ребенка: {data['name'][0]}')
        st.write(f'ФИО родителя: {data['parent_main_name'][0]}')
        st.write(f'Телефон для связи: {data['parent_main_phone'][0]}')
        st.divider()
        st.write(f'ФИО другого взрослого: {data['parent_add'][0]}')
        st.write(f'Телефон для запасной связи: {data['phone_add'][0]}')

        if data['leave'][0] == 'нет':
            st.markdown(f'Уходит сам: :red-background[{data['leave'][0]}]')
        elif data['leave'][0] == 'да':
            st.markdown(f'Уходит сам: :green-background[{data['leave'][0]}]')
        else:
            st.markdown(f'Уходит сам: :blue-background[{data['leave'][0]}]')

        st.write(f'Кто может забирать: {data['additional_contact'][0]}')
        st.write(f'Адрес проживания: {data['addr'][0]}')
        st.write(f'Номер полиса: {data['oms'][0]}')

with col2:
    with st.container(border=True, height=600):
        st.subheader('⚕️ Данные о здоровье')
        st.divider()

        if data['disease'][0] == 'заболеваний нет':
            st.markdown(f'Заболевания: :green-background[{data['leave'][0]}]')
        else:
            st.markdown(f'Заболевания: :red-background[{data['disease'][0]}]')

        if data['allergy'][0] == 'нет':
            st.markdown(f'Аллергия: :green-background[{data['allergy'][0]}]')
        else:
            st.markdown(f'Аллергия: :red-background[{data['allergy'][0]}]')

        if data['other'][0] == 'нет':
            st.markdown(f'Травмы: :green-background[{data['other'][0]}]')
        else:
            st.markdown(f'Травмы: :red-background[{data['other'][0]}]')

        if data['physic'][0] == 'нет':
            st.markdown(f'Орграничения: :green-background[{data['physic'][0]}]')
        else:
            st.markdown(f'Орграничения: :red-background[{data['physic'][0]}]')

with col3:
    with st.container(border=True, height=600):
        st.subheader('📝 Дополнительно')
        st.divider()

        if data['swimm'][0] == 'да':
            st.markdown(f'Будет ли посещать бассейн: :green-background[{data['swimm'][0]}]')
        else:
            st.markdown(f'Будет ли посещать бассейн: :red-background[{data['swimm'][0]}]')

        if data['jacket_swimm'][0] == 'нет':
            st.markdown(f'Нужны ли нарукавники: :green-background[{data['jacket_swimm'][0]}]')
        else:
            st.markdown(f'Нужны ли нарукавники: :red-background[{data['jacket_swimm'][0]}]')

        st.write(f'Чем увлекается: {data['hobby'][0]}')
        st.write(f'Школа: {data['school'][0]}')
        st.divider()
        st.write(f'Доп. информация: {data['additional_info'][0]}')

with st.container(border=True):
    st.subheader('✉️ Общие данные')
    st.write(f'Как узнали про Городок: {data['referer'][0]}')
    st.write(f'e-mail: {data['email'][0]}')
    st.write(f'Прогулки: {data['departures'][0]}')
    st.write(f'Рассылки: {data['mailing'][0]}')
    st.write(f'Согласие на обрботку персональных данных: {data['personal_accept'][0]}')


def create_ds(df):
    output = BytesIO()

    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin'))

    wb = Workbook()
    wb.remove(wb.active)

    ws = wb.create_sheet("Анкета")

    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 42

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="ФИО ребенка")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['name'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Дата рождения ребенка")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['child_birthday'][0].strftime('%d.%m.%Y'))
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="ФИО родителя (законного представителя) для основной связи")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['parent_main_name'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Телефон для основной связи")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['parent_main_phone'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="ФИО другого взрослого")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['parent_add'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Телефон для запасной связи")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['phone_add'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Ребенок будет уходить сам по окончании дня?")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['leave'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Кто кроме родителя (законного представителя) может забирать "
                                                     "ребенка? ФИО, кем приходится, контактный телефон.")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['additional_contact'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Адрес фактического проживания ребенка")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['addr'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Номер страхового медицинского полиса")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['oms'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Сведения о состоянии здоровья ребенка:")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    ws.merge_cells(start_row=num_rows + 1, start_column=1, end_row=num_rows + 1, end_column=2)

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Есть ли у ребенка заболевания (сердца, пищеварительной системы, "
                                                     "нервной системы, психические расстройства, опорно-двигательной "
                                                     "системы, внутренних органов). Если есть, поясните подробнее.")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['disease'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Есть ли у ребенка аллергическая реакция (если есть, укажите, "
                                                     "на что и как она проявляется): ")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['allergy'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Были ли у ребенка (Операции, Переломы, Сотрясение мозга, "
                                                     "Приступы эпилепсии). Если да, поясните подробнее.")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['other'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Есть ли у ребенка ограничения по физическим нагрузкам? Если да, "
                                                     "поясните подробнее.")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['physic'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Дополнительные сведения")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    ws.merge_cells(start_row=num_rows + 1, start_column=1, end_row=num_rows + 1, end_column=2)

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Будет ли ребенок посещать бассейн во время смены?")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['swimm'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Нужны ли ребенку в бассейне нарукавники или жилет?")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['jacket_swimm'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Чем увлекается Ваш ребенок? (хобби, любимое занятие)")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['hobby'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Какое учебное заведение посещает ребенок?")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['school'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Если вы хотите еще что-то рассказать нам о своем ребенке, "
                                                     "напишите это здесь")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['additional_info'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Как Вы узнали про клуб Городок?")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['referer'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row

    cell = ws.cell(row=num_rows + 1, column=1, value="Ваш email:")
    cell.font = Font(name='TimesNewRoman', size=9, bold=True)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    cell = ws.cell(row=num_rows + 1, column=2, value=df['email'][0])
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

    num_rows = ws.max_row + 1

    text = f"Я, {df['parent_main_name'][0]}, законный представитель несовершеннолетнего гражданина"
    cell = ws.cell(row=num_rows + 1, column=1, value=text)
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.merge_cells(start_row=num_rows + 1, start_column=1, end_row=num_rows + 1, end_column=2)

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=1,
                   value=f"___________________________________________ {df['child_birthday'][0].strftime('%d.%m.%Y')} г.р.")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.merge_cells(start_row=num_rows, start_column=1, end_row=num_rows, end_column=2)

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=1, value="Подтверждаю предоставленные мной сведения")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    cell = ws.cell(row=num_rows, column=2, value="____________________")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    ws.row_dimensions[num_rows].height = 30

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=2, value="(подпись)")
    cell.font = Font(name='TimesNewRoman', size=8)
    cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=1, value="даю свое согласие на получение информационных сообщений от детского "
                                                 "клуба Городок")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    cell = ws.cell(row=num_rows, column=2, value="____________________")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    ws.row_dimensions[num_rows].height = 30

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=2, value="(подпись)")
    cell.font = Font(name='TimesNewRoman', size=8)
    cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=1, value="подтверждаю свое согласие на обработку своих персональных данных и"
                                                 "своего ребенка ")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    cell = ws.cell(row=num_rows, column=2, value="____________________")
    cell.font = Font(name='TimesNewRoman', size=9)
    cell.alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)

    ws.row_dimensions[num_rows].height = 30

    num_rows = ws.max_row + 1

    cell = ws.cell(row=num_rows, column=2, value="(подпись)")
    cell.font = Font(name='TimesNewRoman', size=8)
    cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

    wb.save(output)
    output.seek(0)
    return output


if st.button("📎 Скачать анкету в .xlsx"):
    excel_file = create_ds(data)
    st.download_button(
        label="💾Нажми для скачивания анкеты",
        data=excel_file,
        file_name=f"Анкета_{data['name'][0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
