import xlsxwriter

from db_data_users import MongoDB

FILE_NAME = 'test'
db = MongoDB()
workbook = xlsxwriter.Workbook(FILE_NAME + '.xlsx')
worksheet = workbook.add_worksheet('test')

worksheet.write(0, 0, 'users')

def get_username(user):
    username = user.get('username', None)
    if username:
        return username
    first_name = user.get('first_name', None)
    if first_name:
        last_name = user.get('last_name', None)
        if last_name:
            return first_name + ' ' + last_name
        return first_name
    return 'Гость'

col = 1
for user in db.get_all_bets():
    worksheet.write(0, col, get_username(user['user']))
    col += 1

workbook.close()
