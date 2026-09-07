import openpyxl

from config.config import *


def read_excel(file_path, sheet_name):
    workbook = openpyxl.load_workbook(file_path)

    worksheet = workbook[sheet_name]

    data = []

    # 列表推导式
    keys = [cell.value for cell in worksheet[2]]

    for row in worksheet.iter_rows(min_row=3, values_only=True):
        # print(row)
        dict_data = dict(zip(keys, row))
        if dict_data["is_true"]:
            data.append(dict_data)


    workbook.close()

    return data
