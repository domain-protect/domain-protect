from utils.utils_aws import publish_to_sns
from utils.utils_db import count_previous_month
from utils.utils_db import count_previous_year
from utils.utils_db import db_get_table_name
from utils.utils_db_ips import db_count_items


def lambda_handler(event, context):  # pylint:disable=unused-argument

    json_data = {
        "LastMonth": count_previous_month(),
        "LastYear": count_previous_year(),
        "Total": db_count_items(db_get_table_name()),
    }

    publish_to_sns(json_data, "Monthly Stats")
