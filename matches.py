from db import FCDataBase

list_matches = []
date_first_match = None
matches_in_db = FCDataBase()
matches_in_db.query(
    """SELECT home_team_id, away_team_id, time_match FROM football_championsleaguematches WHERE start_year = %s AND status = %s ORDER BY time_match;""",
    (2019, 'SCHEDULED'))

for match in matches_in_db.cursor:

    club_name_in_db = FCDataBase()

    if not date_first_match:
        date_first_match = match[2].date()
    else:
        delta = match[2].date() - date_first_match

        if delta.days > 2:
            break

    match_string = ''
    blank = False

    for team_id in match[:2]:

        club_name_in_db.query("""SELECT club_name FROM football_dictionaryclubname WHERE id = 
                      (SELECT fc_id_name_dictionary_id FROM football_footballclub WHERE id = %s);""", (team_id,))

        for club_name in club_name_in_db.cursor:
            match_string += club_name[0]

            if not blank:
                match_string += ' - '
                blank = True
            else:
                blank = False

    list_matches.append(match_string)
    club_name_in_db.close()
matches_in_db.close()
