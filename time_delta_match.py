from datetime import datetime


MAX_HOURS_BEFORE_BET = 2


def delta_time(date_match):
    delta = datetime.now() - date_match
    if delta.days == 0:
        hours = delta.seconds // 3600
        if hours > MAX_HOURS_BEFORE_BET:
            return True
    elif delta.days < 0:
        return True
    return False
