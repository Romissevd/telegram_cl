from api_matches import FCDataBase


def loading_matches_from_db():
    list_matches = []
    date_first_match = None
    matches_in_db = FCDataBase()
    matches_in_db.query(
        """SELECT home_team_id, away_team_id, time_match FROM football_championsleaguematches WHERE start_year = %s AND status = %s ORDER BY time_match;""",
        (2019, 'SCHEDULED'))

    for match in matches_in_db.cursor:

        if not date_first_match:
            date_first_match = match[2].date()
        else:
            delta = match[2].date() - date_first_match

            if delta.days > 2:
                break

        match_string = text_match(match[:2])
        list_matches.append(match_string)
    matches_in_db.close()
    return list_matches


def text_match(lst_num_club):
    real_clubs_name = []
    for club in lst_num_club:
        real_clubs_name.append(load_club_name(club))
    return ' - '.join(real_clubs_name)


def load_club_name(team_id):

    club_name_in_db = FCDataBase()

    club_name_in_db.query("""SELECT club_name FROM football_dictionaryclubname WHERE id = 
                  (SELECT fc_id_name_dictionary_id FROM football_footballclub WHERE id = %s);""", (team_id,))

    for club_name in club_name_in_db.cursor:
        club_name_in_db.close()
        return club_name[0]
