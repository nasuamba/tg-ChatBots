import pandas as pd

MTR = pd.read_excel("Вход.XLSX", sheet_name="Лист1")
BOT_TOKEN='BOT_TOKEN'

def is_part_in_list(what, where):
    for word in where:
        if word.lower() in what.lower():
            return True
    return False