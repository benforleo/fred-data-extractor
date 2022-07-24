import logging
from datetime import datetime, timedelta
import requests
import boto3

logger = logging.getLogger()

class FredExtractor:
    data = None

    def __init__(self, event, context, session: boto3.Session) -> None:
        self.event = event
        self.context = context
        self.session = session

    def request_fred_data(self, series_id):
        url = "https://api.stlouisfed.org/fred/series/observations"
        observation_date = self.generate_query_date(self.event)

        params = {
            'series_id': series_id,
            'frequency': 'd',
            'observation_start': observation_date,
            'observation_end': observation_date,
            'api_key': self.retrieve_api_key()
        }
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            self.data = r.json()
        except requests.exceptions.RequestException as err:
            raise err
        return self

    def store_fred_data_in_s3(self, bucket):
        if len(self.data['observations']) == 0:
            logger.info("No data to save today")
        else:
            client = self.session.client("s3")
            response = client.put_object(
                Bucket=bucket,
                Key="fred/SP500/year={}/month={}/SP500-{}.json",
                Body=self.data
            )

    def retrieve_api_key(self):
        client = self.session.client(
            service_name='secretsmanager'
        )
        response = client.get_secret_value(
            SecretId="dev/FredExtractor/APIKey"
        )
        return response['SecretString']['fred-api-key']

    @staticmethod
    def generate_query_date(event):
        event_datetime = datetime.strptime(event['time'], "%Y-%m-%dT%H:%M:%SZ")
        query_datetime = event_datetime - timedelta(days=1)
        return query_datetime.strftime("%Y-%m-%d")




