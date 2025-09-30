import streamlit as st
import pandas as pd
from sql import Records, Groups, session_scope

st.title("Records Editor")
permissions = st.session_state.user_permissions.reset_index()
a = permissions['editing_users'][0]

# # --- 1. Загружаем группы ---
# group_names = Groups.get_groups()  # список всех групп из Groups
#
# # --- 2. Загружаем записи ---
# df = Records.get_df()
#
# # --- 3. Пивотируем данные: child_name + parent_name слева, группы - столбцами ---
# pivot = df.pivot_table(
#     index=["child_name", "parent_name"],
#     columns="group_name",
#     values="record_status",
#     aggfunc="first"
# ).reset_index()
#
# # --- 4. Добавляем отсутствующие группы ---
# for g in group_names:
#     if g not in pivot.columns:
#         pivot[g] = ""
#
# # --- 5. Заменяем NaN на пустую строку только в колонках групп ---
# group_cols = [g for g in group_names]
# pivot[group_cols] = pivot[group_cols].fillna("")
#
# # --- 6. Редактор ---
# editor_df = st.data_editor(
#     pivot,
#     key="records_editor",
#     num_rows="dynamic",
# )
#
# # --- 7. Сохранение изменений ---
# if st.button("Сохранить изменения"):
#     with session_scope() as session:
#         # Melt обратно в длинный формат
#         long_df = editor_df.melt(
#             id_vars=["child_name", "parent_name"],
#             value_vars=group_cols,
#             var_name="group_name",
#             value_name="record_status"
#         )
#
#         # Заменяем None на пустую строку и фильтруем пустые статусы
#         long_df["record_status"] = long_df["record_status"].fillna("")
#         long_df = long_df[long_df["record_status"] != ""]
#
#         for _, row in long_df.iterrows():
#             # Проверяем, есть ли запись
#             record = session.query(Records).filter_by(
#                 child_name=row["child_name"],
#                 parent_name=row["parent_name"],
#                 group_name=row["group_name"]
#             ).first()
#             if record:
#                 # Обновляем существующую запись
#                 record.record_status = row["record_status"]
#             else:
#                 # Создаём новую запись
#                 new_record = Records(
#                     child_name=row["child_name"],
#                     parent_name=row["parent_name"],
#                     group_name=row["group_name"],
#                     record_status=row["record_status"]
#                 )
#                 session.add(new_record)
#         session.commit()
#     st.success("Изменения сохранены!")
#     st.rerun()
#
# # --- 8. Удаление выбранных строк ---
# if st.button("Удалить выбранные строки"):
#     selected_rows = editor_df.index[editor_df.get("__selected__", pd.Series(False))]
#     with session_scope() as session:
#         for idx in selected_rows:
#             row = editor_df.loc[idx]
#             # Удаляем все записи ребенка + родителя
#             records_to_delete = session.query(Records).filter_by(
#                 child_name=row["child_name"],
#                 parent_name=row["parent_name"]
#             ).all()
#             for record in records_to_delete:
#                 session.delete(record)
#         session.commit()
#     st.success("Выбранные записи удалены!")
#     st.rerun()
