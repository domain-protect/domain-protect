from datetime import datetime
from utils.utils_dates import calc_prev_month_start


def test_last_month_start_returns_first_of_previous_month():
    input_date = datetime(2022, 3, 5)
    expected = datetime(2022, 2, 1)

    result = calc_prev_month_start(input_date)

    assert result == expected
