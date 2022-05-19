from utils.utils_db import count_previous_month, count_previous_year, db_get_table_name
from utils.utils_db_ips import db_count_items
from utils.utils_aws import publish_to_sns


def lambda_handler(event, context):  # pylint:disable=unused-argument

    json_data = {
        "LastMonth": count_previous_month(),
        "LastYear": count_previous_year(),
        "Total": db_count_items(db_get_table_name()),
    }

    publish_to_sns(json_data, "Monthly Stats")
