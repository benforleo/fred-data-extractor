import json
import boto3
from fred_extractor import FredExtractor


def handler(event, context):
    # session = boto3.session.Session()
    # FredExtractor(session).retrieve_api_key()

    return {'message': 'Hello world!'}
