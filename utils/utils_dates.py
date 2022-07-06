from dateutil.relativedelta import relativedelta


def calc_prev_month_start(date):
    month_in_past = date - relativedelta(months=1)
    return month_in_past.replace(day=1, hour=0, minute=0, second=0)
