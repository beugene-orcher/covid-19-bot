import boto3

from chalicelib.configer import (
    SNS_TOPIC_FOR_COVID_CASES,
    DDB_CONFIG_TABLE_NAME,
    DDB_CASES_TABLE_NAME
)


def get_ddb():
    return boto3.client('dynamodb')


def get_sns():
    return boto3.client('sns')


def create_sns_topic():
    if check_sns_topic_config():
        raise Exception('cannot create sns topic, is existed in config table')
    sns = get_sns()
    topic = sns.create_topic(Name=SNS_TOPIC_FOR_COVID_CASES)
    put_sns_arn_to_config(topic['TopicArn'])


def create_config_table():
    ddb = get_ddb()
    if check_config_table():
        raise Exception('config table is found, cannot recreate the table')
    ddb.create_table(
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


def create_cases_table():
    ddb = get_ddb()
    if check_cases_table():
        raise Exception('config table is found, cannot recreate the table')
    ddb.create_table(
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


def check_config_table():
    ddb = get_ddb()
    if DDB_CONFIG_TABLE_NAME in ddb.list_tables()['TableNames']:
        return True
    return False


def check_cases_table():
    ddb = get_ddb()
    if DDB_CASES_TABLE_NAME in ddb.list_tables()['TableNames']:
        return True
    return False


def check_sns_topic_config():
    ddb = get_ddb()
    if not check_config_table():
        raise Exception('cannot check sns topic, config table is not found')
    item = ddb.get_item(
        TableName=DDB_CONFIG_TABLE_NAME,
        Key={
            'param': {
                'S': 'SNS_TOPIC'
            }
        }
    )
    if item.get('Item'):
        return True
    return False


def get_sns_arn():
    ddb = get_ddb()
    arn = ddb.get_item(
        TableName=DDB_CONFIG_TABLE_NAME,
        Key={
            'param': {
                'S': 'SNS_TOPIC'
            }
        }
    )['Item']['arn']
    return arn


def put_sns_arn_to_config(arn):
    ddb = get_ddb()
    ddb.put_item(
        TableName=DDB_CONFIG_TABLE_NAME,
        Item={
            'param': {
                'S': 'SNS_TOPIC'
            },
            'arn': {
                'S': arn
            }
        }
    )