**covid19bot** is a AWS Lambda application based on AWS Services: Lambda, DynamoDB, API Gateway, SNS, CloudWatch for grabbing official coronavirus sources, processing and storing in a database. It provides an HTTP JSON API and Telegram API for returning results.

The project is in progress.

## Installation

Local environment:
1) create AWS account and set AWS credentials (__https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html__)
2) run `cp .chalice/config.json.template .chalice/config.json`
3) create and activate a virtualenv
4) install dependencies from `requirements.txt`
5) run create-aws-schema.py (creates required artefacts, is used only for initializing before a first launch)
6) run `chalice local`

By default, chalice is starting on *http://127.0.0.1:8000*
The local environment is limited but provides HTTP JSON API for some actions.

AWS environment:
1) create AWS account and set AWS credentials (__https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html__)
2) run `cp .chalice/config.json.template .chalice/config.json`
3) create and activate a virtualenv
4) install dependencies from `requirements.txt`
5) install vendor dependencies `pip3 install tornado==6.0.4 -p vendor` (AWS Lambda doesn't support the package for building, but it can be changed in the future)
6) (optional) set telegram token issued by @botfather in `.chalice/config.json`
7) run `chalice deploy`

By default, the chalice shows you the resources which were deployed and API URL in AWS API Gateway.

## Telefram integration

If you want to connect the application to telegram:
1) set telegram token issued by @botfather in `.chalice/config.json`
2) after deploying, send a HTTP POST request to `{server}/{api_gateway_stage}/mgmt/webhook
Notic: {server} is running by your `chalice deploy` and {api_gateway_stage} is declared in `.chalice/config.json` (`api` by default).