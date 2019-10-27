TOKEN = None

with open('config') as config:
    for row in config.readlines():
        if 'TOKEN' in row:
            row = row.replace('TOKEN', '').replace('=', '').strip()
            if row:
                TOKEN = row
