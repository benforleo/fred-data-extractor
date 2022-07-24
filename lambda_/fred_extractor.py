import logging
from datetime import datetime, timedelta
import json
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FredExtractor:
    data = None

    def __init__(self, event, context, session: boto3.Session, bucket, series_id="SP500") -> None:
        self.event = event
        self.context = context
        self.session = session
        self.bucket = bucket
        self.series_id = series_id
        self.observation_date = self.generate_observation_date(event)

    def execute(self):
        self.request_fred_data() \
            .store_fred_data_in_s3()

    def request_fred_data(self):
        logger.info("[FredExtractor][request_fred_data] has been called")

        url = "https://api.stlouisfed.org/fred/series/observations"
        observation_datestring = self.observation_date.strftime("%Y-%m-%d")
        params = {
            'series_id': self.series_id,
            'frequency': 'd',
            'observation_start': observation_datestring,
            'observation_end': observation_datestring,
            'api_key': self.retrieve_api_key(),
            'file_type': 'json'
        }
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            self.data = r.json()
        except requests.exceptions.RequestException as err:
            raise err
        return self

    def store_fred_data_in_s3(self):
        if len(self.data['observations']) == 0:
            logger.info("No data to save today")
        else:
            client = self.session.client("s3")
            object_key = self.generate_s3_object_key()

            response = client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=json.dumps(self.data)
            )

    def retrieve_api_key(self):
        client = self.session.client(service_name='secretsmanager')
        response = client.get_secret_value(SecretId="dev/FredExtractor/APIKey")
        secret = json.loads(response['SecretString'])
        return secret['fred-api-key']

    def generate_s3_object_key(self):
        year = str(self.observation_date.year)
        month = str(self.observation_date.month).rjust(2, "0")
        observation_datestring = self.observation_date.strftime("%Y-%m-%d")
        return f"fred/{self.series_id}/year={year}/month={month}/{self.series_id}-{observation_datestring}.json"

    @staticmethod
    def generate_observation_date(event: dict) -> datetime:
        event_datetime = datetime.strptime(event['time'], "%Y-%m-%dT%H:%M:%SZ")
        observation_datetime = event_datetime - timedelta(days=1)
        return observation_datetime
