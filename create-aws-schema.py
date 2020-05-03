from time import sleep

from chalicelib.sns_manage import create_sns_topic
from chalicelib.ddb_manage import (
    create_config_table,
    create_cases_table,
    create_total_table
)


try:
    # TODO: add forcing
    print('Preparing artefacts before chalice deploy...')
    print('Creating entities in DynamoDB...')
    create_config_table()
    create_cases_table()
    create_total_table()
    # TODO: add waiters in create_table... and remove sleeping
    sleep(5)
    print('Creating entities in SNS...')
    create_sns_topic()
except Exception:
    raise
