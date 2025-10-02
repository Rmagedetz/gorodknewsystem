import gspread
import pandas as pd
from connections import google_sheet_credit_nails

gc = gspread.service_account_from_dict(google_sheet_credit_nails)


def get_quiz_data():
    google_data = gc.open("Анкета ребёнка межсезон 24-25")
    sheet = google_data.worksheet("Лист1")
    all_values = sheet.get_all_values()

    df = pd.DataFrame(all_values).iloc[2:, :-6]
    df.columns = ["email", "name", "child_birthday", "parent_main_name", "parent_main_phone", "parent_add",
                  "phone_add", "leave", "additional_contact", "addr", "disease", "allergy", "other", "physic",
                  "swimm", "jacket_swimm", "hobby", "school", "additional_info", "departures", "referer", "ok",
                  "mailing", "personal_accept", "oms"]
    # df["age"] = 0
    return df