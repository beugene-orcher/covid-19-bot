"""
"""
from datetime import datetime, timedelta

import boto3

from boto3.dynamodb.conditions import Key
from chalicelib.configer import (
    DDB_CONFIG_TABLE_NAME,
    DDB_CASES_TABLE_NAME,
    DDB_TOTAL_TABLE_NAME,
    REGIONS,
    MAX_DEEP_DAY
)


class DDBObject(object):
    resource = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')


ddb = DDBObject()


def create_config_table():
    """Create config table, uses only for init db"""
    try:
        check_config_table()
        raise DDBConfigTableAlreadyCreated()
    except DDBConfigTableNotFound:
        ddb.client.create_table(
            TableName=DDB_CONFIG_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'param',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'param',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except Exception:
        raise


def create_cases_table():
    """Create cases table, uses only for init db"""
    try:
        check_cases_table()
        raise DDBCasesTableAlreadyCreated
    except DDBCasesTableNotFound:
        ddb.client.create_table(
            TableName=DDB_CASES_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'actual_date',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'region',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'actual_date',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'region',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except Exception:
        raise


def create_total_table():
    """Create total table, uses only for init db"""
    try:
        check_total_table()
        raise DDBTotalTableAlreadyCreated
    except DDBTotalTableNotFound:
        ddb.client.create_table(
            TableName=DDB_TOTAL_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'actual_date',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'region',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'actual_date',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'region',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except Exception:
        raise


def check_config_table():
    """Checker config table"""
    if DDB_CONFIG_TABLE_NAME not in ddb.client.list_tables()['TableNames']:
        raise DDBConfigTableNotFound()


def check_cases_table():
    """Checker cases table"""
    if DDB_CASES_TABLE_NAME not in ddb.client.list_tables()['TableNames']:
        raise DDBCasesTableNotFound()


def check_total_table():
    """Checker total table"""
    if DDB_TOTAL_TABLE_NAME not in ddb.client.list_tables()['TableNames']:
        raise DDBTotalTableNotFound()


def put_sns_arn(arn):
    """Putting a given arn of SNS Topic to config table"""
    try:
        if get_sns_arn():
            raise DDBConfigSNSFound()
    except DDBConfigSNSNotFound:
        ddb.resource.Table(DDB_CONFIG_TABLE_NAME).put_item(
            Item={
                'param': 'SNS_TOPIC',
                'arn': arn
            }
        )
    except Exception:
        raise


def get_sns_arn():
    """Getting an existed arn of SNS Topic from config table"""
    try:
        check_config_table()
        arn = ddb.resource.Table(DDB_CONFIG_TABLE_NAME).get_item(
            Key={'param': 'SNS_TOPIC'}
        )['Item']['arn']
        return arn
    except KeyError:
        raise DDBConfigSNSNotFound()
    except Exception:
        raise


def get_last_record_by_region(region, table):
    """Returns total cases in region"""
    try:
        if region not in REGIONS:
            raise DDBUnknownRegion()
        check_total_table()
        base = datetime.utcnow()
        for date in [base - timedelta(days=x) for x in range(MAX_DEEP_DAY)]:
            filtering_exp = Key(
                'actual_date').eq(date.isoformat().split('T')[0]) & Key(
                    'region').eq(region)
            result = ddb.resource.Table(table).query(
                KeyConditionExpression=filtering_exp,
                Limit=1
            )['Items']
            if len(result) > 0:
                return result[0]
        raise DDBNoCases(region)
    except Exception:
        raise


def get_new_cases(region):
    """Returns new cases in region"""
    try:
        check_cases_table()
    except Exception:
        raise


class DDBException(Exception):

    def __init__(self, message):
        super().__init__(message)


class DDBConfigTableNotFound(DDBException):

    def __init__(self):
        message = 'Config table is not created'
        super().__init__(message)


class DDBCasesTableNotFound(DDBException):

    def __init__(self):
        message = 'Cases table is not created'
        super().__init__(message)


class DDBTotalTableNotFound(DDBException):

    def __init__(self):
        message = 'Total table is not created'
        super().__init__(message)


class DDBConfigTableAlreadyCreated(DDBException):

    def __init__(self):
        message = 'Config table is existed, cannot be recreated'
        super().__init__(message)


class DDBCasesTableAlreadyCreated(DDBException):

    def __init__(self):
        message = 'Cases table is existed, cannot be recreated'
        super().__init__(message)


class DDBTotalTableAlreadyCreated(DDBException):

    def __init__(self):
        message = 'Total table is existed, cannot be recreated'
        super().__init__(message)


class DDBConfigSNSNotFound(DDBException):

    def __init__(self):
        message = 'SNS ARN not found, must be created before'
        super().__init__(message)


class DDBConfigSNSFound(DDBException):

    def __init__(self):
        message = 'SNS ARN is found, cannot be recreated'
        super().__init__(message)


class DDBUnknownRegion(DDBException):

    def __init__(self):
        message = 'Region is not supported'
        super().__init__(message)


class DDBNoCases(DDBException):

    def __init__(self, region):
        message = f'No covid records for last {MAX_DEEP_DAY} days in {region}'
        super().__init__(message)
