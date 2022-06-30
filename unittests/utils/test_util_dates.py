from datetime import datetime
from utils.utils_dates import calc_prev_month_start
from assertpy import assert_that


def test_calc_prev_month_start_returns_first_of_previous_month():
    input_date = datetime(2022, 3, 5)
    expected = datetime(2022, 2, 1)

    result = calc_prev_month_start(input_date)

    assert_that(result).is_equal_to(expected)


def test_calc_prev_month_start_returns_december_for_jan():
    input_date = datetime(2022, 1, 5)
    expected = datetime(2021, 12, 1)

    result = calc_prev_month_start(input_date)

    assert_that(result).is_equal_to(expected)
