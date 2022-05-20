import datetime
from dateutil.relativedelta import relativedelta


def last_month_start():
    month_in_past = datetime.datetime.now() - relativedelta(months=1)
    return month_in_past.replace(day=1, hour=0, minute=0, second=0)
