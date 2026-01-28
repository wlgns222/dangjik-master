import calendar
from datetime import datetime, date, timedelta

FORM = "%Y-%m-%d"

def get_formatted_date(y, m, d):
    dt_obj = date(y, m, d)
    return dt_obj.strftime(FORM)

def get_date_list(year, month):
    return [day.strftime("%Y-%m-%d") for week in calendar.Calendar().monthdatescalendar(year, month)  for day in week if day.month == month]

def is_date_in_range(target_date, start_date, end_date):
    return start_date <= target_date <= end_date

def get_date_diff(date_str_a, date_str_b):
    d1 = datetime.strptime(date_str_a, FORM)
    d2 = datetime.strptime(date_str_b, FORM)
    return abs((d2 - d1).days)

def get_custom_date_list(start_str, end_str):
    start = datetime.strptime(start_str, FORM)
    end = datetime.strptime(end_str, FORM)
    
    date_list = []
    curr = start
    while curr <= end:
        date_list.append(curr.strftime(FORM))
        curr += timedelta(days=1)
    return date_list