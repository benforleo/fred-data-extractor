import os
import boto3
from lambda_.functions.extract.fred_extractor import FredExtractor

bucket = os.getenv("FRED_BUCKET_NAME")


def handler(event, context):
    session = boto3.session.Session()

    try:
        fred = FredExtractor(
            event,
            context,
            session,
            bucket,
            series_id="SP500"
        )
        response = fred.execute()
        return response

    except Exception as err:
        raise err
