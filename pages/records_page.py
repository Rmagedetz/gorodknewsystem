import datetime
from dateutil.relativedelta import relativedelta

import streamlit as st
import pandas as pd

import sql
from sql import Records, session_scope

permission = st.session_state.user_permissions['editing_records'][0]

# --- Выбор сезона ---
seasons = sql.Seasons.get_df()['season_name']
season_selector = st.selectbox('Сезон', seasons)

# --- Загружаем данные ---
df = Records.get_df(season_name=season_selector)

# --- Считаем статистику по группам ---
stats = sql.Groups.get_df(season_name=season_selector)
group_counts = (
    df
    .groupby('group_name')
    .agg(
        reserved=('record_id', 'count'),
        paid=('record_status', lambda x: x.astype(str).str.contains('о').sum())
    )
    .reset_index()
)

merged = stats.merge(group_counts, on='group_name', how='left')

# Добавляем places_left и форматируем
merged['reserved'] = merged['reserved'].fillna(0).astype(int)
merged['paid'] = merged['paid'].fillna(0).astype(int)
merged['places_left'] = merged['capacity'] - merged['reserved']
merged['capacity'] = merged['capacity'].astype(int)

merged['start_date'] = pd.to_datetime(merged['start_date']).dt.strftime('%d.%m.%y')
merged['end_date'] = pd.to_datetime(merged['end_date']).dt.strftime('%d.%m.%y')

merged = merged.rename(columns={
    'filial_name': 'Филиал',
    'start_date': 'Дата начала',
    'end_date': 'Дата окончания',
    'reserved': 'Забронировано',
    'paid': 'Оплачено',
    'places_left': 'Свободно'
})

# --- Список групп в нужном порядке ---
group_names = sql.Groups.get_df(season_name=season_selector)['group_name'].tolist()

# Оставляем только нужные колонки
cols_to_keep = ['group_name', 'Филиал', 'Дата начала', 'Дата окончания', 'Забронировано', 'Оплачено', 'Свободно']
merged = merged[[c for c in cols_to_keep if c in merged.columns]]

# --- Преобразуем merged в "параметры-строки" ---
merged_melted = merged.melt(
    id_vars='group_name',
    var_name='Параметр',
    value_name='Значение'
)

result_df = merged_melted.pivot(
    index='Параметр',
    columns='group_name',
    values='Значение'
)

# Переставляем колонки result_df строго по group_names
result_df = result_df[group_names]
result_df = result_df.reset_index()

# --- Приводим все колонки групп к строкам, чтобы PyArrow не ругался ---
result_df.iloc[:, 1:] = result_df.iloc[:, 1:].astype(str)

# --- Показываем hat ---
col_config_hat = {
    "Параметр": st.column_config.TextColumn("Параметр", width=440, disabled=True)
}
for g in group_names:
    col_config_hat[g] = st.column_config.TextColumn(g)
hat = st.data_editor(result_df, hide_index=True, column_config=col_config_hat)

# --- Формируем pivot ---
pivot = df.pivot_table(
    index=["child_name", "parent_name"],
    columns="group_name",
    values="record_status",
    aggfunc="first"
).reset_index()

# Создаём пустые колонки для отсутствующих групп
for g in group_names:
    if g not in pivot.columns:
        pivot[g] = None

# Фиксируем порядок колонок
pivot = pivot[["child_name", "parent_name"] + group_names]

# --- Подготовка DataFrame для отображения в редакторе ---
display_df = pivot.copy()
display_df[group_names] = display_df[group_names].mask(display_df[group_names].isna(), "")

col_config_editor = {
    "child_name": st.column_config.TextColumn("Ребёнок", disabled=True, width=200),
    "parent_name": st.column_config.TextColumn("Родитель", disabled=True, width=200),
}
for g in group_names:
    col_config_editor[g] = st.column_config.TextColumn(g)

editor_df = st.data_editor(
    display_df,
    key="records_editor",
    hide_index=True,
    column_config=col_config_editor
)


# --- Добавление записи ---
@st.dialog("Добавление записи", width="medium")
def add_record():
    add_from_ankets = st.checkbox('Добавить из анкет', value=True)
    if not add_from_ankets:
        # --- Родитель ---
        parents = sql.Records.get_unique_parents()

        # по умолчанию — новый родитель
        use_existing_parent = st.checkbox('Родитель уже есть в записях', key='parent_checkbox')

        if use_existing_parent:
            parent = st.selectbox('Родитель', parents, key='parent_selector')
        else:
            parent = st.text_input("Родитель")
            parent_phone_num = st.text_input('Номер телефона', placeholder="+7-(XXX)-XXX-XX-XX")

        # --- Ребёнок ---
        use_existing_child = st.checkbox('Ребенок уже есть в записях', key='child_checkbox')

        if use_existing_child:
            if use_existing_parent:
                # если выбран существующий родитель — показываем детей только этого родителя
                children_for_parent = sql.Records.get_children_for_parent(parent)
                child = st.selectbox('Ребенок', children_for_parent, key='child_selector')
            else:
                # если родитель новый — показываем всех детей из базы
                all_children = sql.Records.get_all_unique_children()  # нужен метод, см. ниже
                child = st.selectbox('Ребенок', all_children, key='child_selector')
        else:
            child = st.text_input('Ребенок')
            child_age = st.text_input('Возраст')
            child_school = st.text_input('Школа')

        if child:
            existing_groups = (
                Records.get_df(
                    season_name=season_selector,
                    child_name=child
                )["group_name"].unique().tolist()
            )
        else:
            existing_groups = []
        info = st.dataframe(hat, hide_index=True)
        available_groups = [g for g in group_names if g not in existing_groups]
        selection = st.pills("Группы", available_groups, selection_mode="multi")
        comment = st.text_area('Комментарий', max_chars=1000)
        if st.button('Добавить запись', key='add_record_accept'):
            for group in selection:
                sql.Records.add_object(
                    season_name=season_selector,
                    filial_name=sql.Groups.get_filial_for_group_in_season(season_selector, group),
                    group_name=group,
                    parent_name=parent,
                    child_name=child,
                    record_status=1,
                    comment=comment
                )
            if not use_existing_child:
                sql.Child.add_object(child_name=child,
                                     parent_name=parent,
                                     child_age=child_age,
                                     school=child_school)
            if not use_existing_parent:
                sql.Parent.add_object(
                    parent_name=parent,
                    parent_phone=parent_phone_num
                )
            st.rerun()
    else:
        ankets_df = sql.Ankets.get_df()
        anket_selector = st.selectbox('Анкета', ankets_df['name'])
        selected_anket = ankets_df[ankets_df['name'] == anket_selector].reset_index()

        selected_anket['child_name'] = selected_anket.pop('name')
        selected_anket['parent_name'] = selected_anket.pop('parent_main_name')

        info = st.dataframe(hat, hide_index=True)
        available_groups = group_names
        selection = st.pills("Группы", available_groups, selection_mode="multi")
        comment = st.text_area('Комментарий', max_chars=1000)

        bd = selected_anket['child_birthday'][0]
        now = datetime.date.today()

        age = relativedelta(now, bd).years

        if st.button('Добавить', key='add_from_ankets_accept'):
            for group in selection:
                sql.Records.add_object(
                    season_name=season_selector,
                    filial_name=sql.Groups.get_filial_for_group_in_season(season_selector, group),
                    group_name=group,
                    parent_name=selected_anket['parent_name'][0],
                    child_name=selected_anket['child_name'][0],
                    record_status=1,
                    comment=comment
                )
            sql.Child.add_object(
                child_name=selected_anket['child_name'][0],
                parent_name=selected_anket['parent_name'][0],
                child_age=age,
                child_birthday=selected_anket['child_birthday'][0],
                parent_add=selected_anket['parent_add'][0],
                phone_add=selected_anket['phone_add'][0],
                leave=selected_anket['leave'][0],
                additional_contact=selected_anket['additional_contact'][0],
                addr=selected_anket['addr'][0],
                disease=selected_anket['disease'][0],
                allergy=selected_anket['allergy'][0],
                other=selected_anket['other'][0],
                physic=selected_anket['physic'][0],
                swimm=selected_anket['swimm'][0],
                jacket_swimm=selected_anket['jacket_swimm'][0],
                hobby=selected_anket['hobby'][0],
                school=selected_anket['school'][0],
                additional_info=selected_anket['additional_info'][0],
                departures=selected_anket['departures'][0],
                referer=selected_anket['referer'][0],
                ok=selected_anket['ok'][0],
                mailing=selected_anket['mailing'][0],
                personal_accept=selected_anket['personal_accept'][0],
                oms=selected_anket['oms'][0]
            )
            try:
                sql.Parent.add_object(
                    parent_name=selected_anket['parent_name'][0],
                    parent_phone=selected_anket['parent_main_phone'][0],
                    email=selected_anket['email'][0]
                )
            except:
                pass
            st.rerun()


# --- Сохранение изменений ---
# Сравниваем логические значения (None vs непустое), а не отображение
editor_logical = editor_df.copy()
editor_logical[group_names] = editor_logical[group_names].replace("", pd.NA)

pivot_compare = pivot.copy()
pivot_compare[group_names] = pivot_compare[group_names].where(pivot_compare[group_names].notna(), pd.NA)

changes_exist = not editor_logical.set_index(["child_name", "parent_name"]).equals(
    pivot_compare.set_index(["child_name", "parent_name"])
)

if st.button("Сохранить изменения", disabled=not changes_exist, width=240):
    with session_scope() as session:
        group_cols = pivot.columns[2:]

        # Melt обратно в длинный формат
        long_df = editor_df.melt(
            id_vars=["child_name", "parent_name"],
            value_vars=group_cols,
            var_name="group_name",
            value_name="record_status"
        )

        for _, row in long_df.iterrows():
            record = session.query(Records).filter_by(
                season_name=season_selector,
                child_name=row["child_name"],
                parent_name=row["parent_name"],
                group_name=row["group_name"]
            ).first()

            if record:
                # Очистка ячейки → удаление записи
                if pd.isna(row["record_status"]) or row["record_status"] == "":
                    session.delete(record)
                else:
                    # Обновляем существующую запись
                    record.record_status = row["record_status"]
            else:
                # Создаём новую запись только если введён непустой статус
                if not pd.isna(row["record_status"]) and row["record_status"] != "":
                    new_record = Records(
                        season_name=season_selector,
                        filial_name=sql.Groups.get_filial_for_group_in_season(
                            season_selector, row["group_name"]
                        ),
                        group_name=row["group_name"],
                        parent_name=row["parent_name"],
                        child_name=row["child_name"],
                        record_status=row["record_status"]
                    )
                    session.add(new_record)

        session.commit()

    st.success("Изменения сохранены!")
    st.rerun()


@st.dialog('Переименование ребенка')
def rename_child():
    parents = sql.Records.get_unique_parents(season_name=season_selector)
    parent_selector = st.selectbox('Родитель', parents)
    children_for_parent = sql.Records.get_children_for_parent(parent_selector,
                                                              season_name=season_selector)
    child_name = st.selectbox('Ребенок', children_for_parent, key='child_selector')
    new_child_name = st.text_input('Новое имя ребенка')
    if st.button('Переименовать', key='rename_child_accept'):
        sql.Records.rename_child(parent_selector, child_name, new_child_name)
        sql.Child.rename_child(parent_selector, child_name, new_child_name)
        st.rerun()


@st.dialog('Переименование родителя')
def rename_parent():
    children = sql.Records.get_all_unique_children()
    child_selector = st.selectbox('Ребенок', children)
    parent_selector = st.selectbox('Родитель',
                                   sql.Records.get_parent_for_child(child_selector))
    new_parent_name = st.text_input('Новое имя для родителя')
    if st.button('Переименовать', key='rename_parent_accept'):
        sql.Records.rename_parent(child_selector, parent_selector, new_parent_name)
        sql.Child.rename_parent(child_selector, parent_selector, new_parent_name)
        sql.Parent.rename_parent(parent_selector, new_parent_name)
        st.rerun()


if st.button('Добавить запись', key='add_record', width=240):
    add_record()

if st.button('Переименновать ребенка', key='rename_child', width=240):
    rename_child()

if st.button('Переименовать родителя', key='rename_parent', width=240):
    rename_parent()
