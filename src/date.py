import calendar

def get_date_list(year, month):
    return [day.strftime("%Y-%m-%d") for week in calendar.Calendar().monthdatescalendar(year, month)  for day in week if day.month == month]


def is_date_in_range(target_date, start_date, end_date):
    return start_date <= target_date <= end_date
