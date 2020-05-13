"""
"""
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

from chalicelib.models import CovidCase, Subscription
from chalicelib.configer import (
    DDB_CONFIG_TABLE_NAME,
    DDB_CASES_TABLE_NAME,
    DDB_TOTAL_TABLE_NAME,
    DDB_SUBSCRIPTIONS_TABLE_NAME
)


class DDBObject(object):
    resource = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')


ddb = DDBObject()


def create_config_table():
    """Create config table, uses only for init db"""
    try:
        check_table(DDB_CONFIG_TABLE_NAME)
        raise DDBTableAlreadyCreated(DDB_CONFIG_TABLE_NAME)
    except DDBTableNotFound:
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
        check_table(DDB_CASES_TABLE_NAME)
        raise DDBTableAlreadyCreated(DDB_CASES_TABLE_NAME)
    except DDBTableNotFound:
        ddb.client.create_table(
            TableName=DDB_CASES_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'region',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'actual_date',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'region',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'actual_date',
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
        check_table(DDB_TOTAL_TABLE_NAME)
        raise DDBTableAlreadyCreated(DDB_TOTAL_TABLE_NAME)
    except DDBTableNotFound:
        ddb.client.create_table(
            TableName=DDB_TOTAL_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'region',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'actual_date',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'region',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'actual_date',
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


def create_subscriptions_table():
    """Create subscriptions table, uses only for init db"""
    try:
        check_table(DDB_SUBSCRIPTIONS_TABLE_NAME)
        raise DDBTableAlreadyCreated(DDB_SUBSCRIPTIONS_TABLE_NAME)
    except DDBTableNotFound:
        ddb.client.create_table(
            TableName=DDB_SUBSCRIPTIONS_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'region',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'chat_id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'region',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'chat_id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except Exception:
        raise


def check_table(name):
    """Checking table by name"""
    if name not in ddb.client.list_tables()['TableNames']:
        raise DDBTableNotFound(name)


def put_sns_arn(arn, topic):
    """Putting a given arn of SNS Topic to a config table"""
    try:
        get_sns_arn(topic)
    except DDBConfigSNSNotFound:
        ddb.resource.Table(DDB_CONFIG_TABLE_NAME).put_item(
            Item={'param': topic, 'arn': arn})
    else:
        raise DDBConfigSNSFound(topic)


def get_sns_arn(topic):
    """Getting an existed arn of SNS Topic from config table"""
    try:
        arn = ddb.resource.Table(DDB_CONFIG_TABLE_NAME).get_item(
            Key={'param': topic})['Item']['arn']
        return arn
    except KeyError:
        raise DDBConfigSNSNotFound(topic)
    except Exception:
        raise


def put_case(model):
    """Putting cases to DynamoDB"""
    try:
        if model.event == 'EVENT_TOTAL_CASES':
            table = DDB_TOTAL_TABLE_NAME
        if model.event == 'EVENT_NEW_CASES':
            table = DDB_CASES_TABLE_NAME
        # TODO: add table is None warning
        get_cases(model.region, table, model.actual_date)
        return False
    except DDBNoCases:
        ddb.resource.Table(table).put_item(Item=model.to_dict())
        return True
    except Exception:
        raise


def get_cases(region, table, date=None):
    """Returns cases by <= date (or current date) in a given region"""
    try:
        if date is None:
            # then the date is now and try to find the neareast date to now
            date = datetime.utcnow().isoformat().split('T')[0]
            filter_exp = Key(
                'region').eq(region) & Key('actual_date').lte(date)  # lte date
        if date is not None:
            # then the date is given and try to find the equaled date
            filter_exp = Key(
                'region').eq(region) & Key('actual_date').eq(date)  # eq date
        result = ddb.resource.Table(table).query(
            KeyConditionExpression=filter_exp,
            Limit=1,
            ScanIndexForward=False
        )['Items']
        if len(result) > 0:
            return CovidCase().from_dict(result[0])
        raise DDBNoCases(region)
    except Exception:
        raise


def put_subscription(model):
    """Putting a given message to subscription table in DynamoDB"""
    try:
        ddb.resource.Table(DDB_SUBSCRIPTIONS_TABLE_NAME).put_item(
            Item=model.to_dict())
    except Exception:
        raise


def get_subscriptions(region, chat_id=None):
    """Getting subscriptions by region and chat_id or all items in region"""
    try:
        subscriptions = []
        filter_exp = Key('region').eq(region)
        if chat_id:
            filter_exp = Key('region').eq(region) & Key('chat_id').eq(chat_id)
        result = ddb.resource.Table(DDB_SUBSCRIPTIONS_TABLE_NAME).query(
            KeyConditionExpression=filter_exp
        )['Items']
        for elem in result:
            subscriptions.append(Subscription().from_dict(elem))
        return subscriptions
    except Exception:
        raise


class DDBException(Exception):

    def __init__(self, message):
        super().__init__(message)


class DDBTableNotFound(DDBException):

    def __init__(self, name):
        message = f'{name} table not found'
        super().__init__(message)


class DDBTableAlreadyCreated(DDBException):

    def __init__(self, name):
        message = f'{name} table is existed, cannot be recreated'
        super().__init__(message)


class DDBConfigSNSNotFound(DDBException):

    def __init__(self, topic):
        message = f'SNS topic {topic} is not found, must be created before'
        super().__init__(message)


class DDBConfigSNSFound(DDBException):

    def __init__(self, topic):
        message = f'SNS topic {topic} is found, cannot be replaced'
        super().__init__(message)


class DDBUnknownRegion(DDBException):

    def __init__(self):
        message = 'Region is not supported'
        super().__init__(message)


class DDBNoCases(DDBException):

    def __init__(self, region):
        message = f'No covid records in {region}'
        super().__init__(message)
