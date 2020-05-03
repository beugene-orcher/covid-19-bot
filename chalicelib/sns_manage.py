import boto3

from chalicelib.ddb_manage import put_sns_arn, get_sns_arn
from chalicelib.configer import SNS_TOPIC_FOR_COVID_CASES


class SNSObject(object):
    resource = boto3.resource('sns')
    client = boto3.client('sns')


sns = SNSObject()


def create_sns_topic():
    """Create SNS topic, uses only for init db"""
    try:
        topic = sns.client.create_topic(Name=SNS_TOPIC_FOR_COVID_CASES)
        arn = topic['TopicArn']
        put_sns_arn(arn)
        return arn
    except Exception:
        raise


def publish_covid_cases(model):
    """Publish message to SNS covid cases topic"""
    try:
        result = sns.client.publish(
            TopicArn=get_sns_arn(),
            Message=model.to_json()
        )['ResponseMetadata']['HTTPStatusCode']
        if not result == 200:
            raise SNSManagePublishError()
    except Exception:
        raise


class SNSManageError(Exception):

    def __init__(self, message):
        super().__init__(message)


class SNSManagePublishError(SNSManageError):

    def __init__(self, model):
        message = f'Cannot publish to SNS the model {model}'
        super().__init__(message)
