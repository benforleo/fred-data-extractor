import logging
from datetime import datetime, timedelta
import json
from functools import reduce
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FredExtractor:

    url = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, event, context, session: boto3.Session, bucket, series_id="SP500") -> None:
        self.event = event
        self.context = context
        self.session = session
        self.bucket = bucket
        self.series_id = series_id
        self.observation_date = self.generate_observation_date(event) if event is not None else None

    def execute(self):
        response = reduce(
            lambda value, method: method(value),
            (
                self.request_fred_data,
                self.store_fred_data_in_s3
            ),
            self.retrieve_api_key()
        )
        return response

    def request_fred_data(self, api_key) -> dict:
        logger.info("[FredExtractor][request_fred_data] has been called")

        observation_date_string = self.observation_date.strftime("%Y-%m-%d")
        params = {
            'series_id': self.series_id,
            'frequency': 'd',
            'observation_start': observation_date_string,
            'observation_end': observation_date_string,
            'api_key': api_key,
            'file_type': 'json'
        }
        try:
            r = requests.get(url=FredExtractor.url, params=params)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as err:
            raise err

    def store_fred_data_in_s3(self, api_response: dict) -> dict:
        logger.info("[FredExtractor][store_fred_data_in_s3] has been called")

        if len(api_response['observations']) == 0:
            logger.info("No data to save today")
            return {"HTTPStatusCode": 200}

        else:
            client = self.session.client("s3")
            object_key = self.generate_s3_object_key()

            response = client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=json.dumps(api_response)
            )
            logger.info(f"Successfully saved data to s3://{self.bucket}/{object_key}")
            return {"HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"]}

    def retrieve_api_key(self) -> str:
        client = self.session.client(service_name='secretsmanager')
        response = client.get_secret_value(SecretId="dev/FredExtractor/APIKey")
        secret = json.loads(response['SecretString'])
        return secret['fred-api-key']

    def generate_s3_object_key(self) -> str:
        year = str(self.observation_date.year)
        month = str(self.observation_date.month).rjust(2, "0")
        observation_date_string = self.observation_date.strftime("%Y-%m-%d")
        return f"fred/{self.series_id}/year={year}/month={month}/{self.series_id}-{observation_date_string}.json"

    @staticmethod
    def generate_observation_date(event: dict) -> datetime:
        event_datetime = datetime.strptime(event['time'], "%Y-%m-%dT%H:%M:%SZ")
        observation_datetime = event_datetime - timedelta(days=1)
        return observation_datetime
