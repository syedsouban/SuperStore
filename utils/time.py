from datetime import datetime, timedelta
def get_time_after(minutes = 0, hours = 0,days = 0):
    return datetime.today() + timedelta(hours=hours, minutes=minutes,days = days)