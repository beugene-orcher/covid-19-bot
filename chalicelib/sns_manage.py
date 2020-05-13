import boto3

from chalicelib.ddb_manage import put_sns_arn, get_sns_arn
from chalicelib.configer import (
    SNS_TOPIC_FOR_COVID_CASES,
    SNS_TOPIC_FOR_SUBSCRIPTIONS,
    SNS_TOPIC_FOR_BOT_NOTIFICATIONS
)


class SNSObject(object):
    resource = boto3.resource('sns')
    client = boto3.client('sns')


sns = SNSObject()


def create_sns_topics():
    """Create SNS topic, uses only for init db"""
    try:
        topic = sns.client.create_topic(Name=SNS_TOPIC_FOR_COVID_CASES)
        arn = topic['TopicArn']
        put_sns_arn(arn, SNS_TOPIC_FOR_COVID_CASES)
        topic = sns.client.create_topic(Name=SNS_TOPIC_FOR_SUBSCRIPTIONS)
        arn = topic['TopicArn']
        put_sns_arn(arn, SNS_TOPIC_FOR_SUBSCRIPTIONS)
        topic = sns.client.create_topic(Name=SNS_TOPIC_FOR_BOT_NOTIFICATIONS)
        arn = topic['TopicArn']
        put_sns_arn(arn, SNS_TOPIC_FOR_BOT_NOTIFICATIONS)
    except Exception:
        raise


def publish_to_sns(model, topic):
    """Publish model (chalicelib.models.BaseModel) to topic"""
    try:
        result = sns.client.publish(
            TopicArn=get_sns_arn(topic),
            Message=model.to_json()
        )['ResponseMetadata']['HTTPStatusCode']
        if not result == 200:
            raise SNSManagePublishError(model)
    except Exception:
        raise


class SNSManageError(Exception):

    def __init__(self, message):
        super().__init__(message)


class SNSManagePublishError(SNSManageError):

    def __init__(self, model):
        message = f'Cannot publish to SNS the model {model}'
        super().__init__(message)
