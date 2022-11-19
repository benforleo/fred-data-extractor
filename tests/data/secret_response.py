import datetime
from dateutil.tz import tzlocal

secret_response = {
    'ARN': 'arn:aws:secretsmanager:us-east-1:123456789101:secret:dev/FredExtractor/APIKey-blah',
    'Name': 'dev/FredExtractor/APIKey',
    'VersionId': '9ce46a80-6ad6-4e13-8930-cdc6a4854c83',
    'SecretString': '{"fred-api-key":"super-secret-key"}',
    'VersionStages': [
        'AWSCURRENT'
    ],
    'CreatedDate': datetime.datetime(2022, 7, 10, 11, 51, 57, 349000, tzinfo=tzlocal()),
    'ResponseMetadata': {
        'RequestId': '334e58a8-85b1-43fe-8d8f-c89900be2ea7',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '334e58a8-85b1-43fe-8d8f-c89900be2ea7',
            'content-type': 'application/x-amz-json-1.1',
            'content-length': '314',
            'date': 'Tue, 26 Jul 2022 12:14:10 GMT'
        },
        'RetryAttempts': 0
    }
}
