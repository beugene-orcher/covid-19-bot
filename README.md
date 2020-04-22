**covid19bot** is an serverless-lambda web application based on AWS Services: Lambda, DynamoDB, API Gateway, SNS for grabbing data from official coronavirus sources, processing data and sending results to Telegram bot or retrieving by HTTP JSON API.

The project is in progress.

## Installation

Local environment:
1) install dependencies from `requirements.txt`.
2) run `chalice local`.

By default, chalice is starting on *http://127.0.0.1:8000*
The local environment is limited in API Telegram and AWS SNS. If you need to test it local, then additionally. install **pyngrok**.

AWS environment:
1) install challice by `pip3 install chalice`
2) run `cp .chalice/config.json.template .chalice/config.json`
3) set AWS credentials by __https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html__
4) install vendor dependencies `pip3 install tornado==6.0.4 -p vendor` (AWS Lambda doesn't support the package for building, but it can be changed in the future)
5) (optional) get telegram token by @botfarther and set it in `.chalice/config.json`
6) run `chalice deploy`

By default, chalice shows you the resources which were deployed and Rest API URL (public URL of AWS API Gateway).

## Description

AWS Lambda is a serverless and stateless service . Unfortunately, the project can work only with AWS Serveless, because the specific dependencies are including. All developed API endpoints will be deployed in Lambda.

AWS API Gateway is a service to deploy your endpoints. You can check this one after __deploying__, the public endpoint root will be `/api` (described in `config.json`).

AWS SNS is a notification service. Topics must be created by management API by manual.

DynamoDB is no-sql database. Tables must be created by management API by manual.
