import xlsxwriter

from bot import get_username
from db_data_users import MongoDB

FILE_NAME = 'test'
db = MongoDB()
workbook = xlsxwriter.Workbook(FILE_NAME + '.xlsx')
worksheet = workbook.add_worksheet('test')

worksheet.write(0, 0, 'users')

row = 1
col = 1
col_matches = 0
for user in db.get_all_bets():
    res_row = 1
    all_matches_tour = db.get_all_matches_tour(user['id_telegram'])
    for match in all_matches_tour:
        if row < len(all_matches_tour) + 1:
            worksheet.write(row, col_matches, match['match'])
            row += 1
        worksheet.write(res_row, col, match['result'])
        res_row += 1
    worksheet.write(0, col, get_username(user['user']))
    col += 1

workbook.close()
