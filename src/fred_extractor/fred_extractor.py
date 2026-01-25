import json
import logging
from typing import Optional

import boto3
import pendulum
import requests
from botocore.exceptions import ClientError
from toolz import pipe

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class FredExtractor:
    """
    Extracts financial data from the Federal Reserve Economic Data (FRED) API
    and stores it in S3 with partitioned structure.
    """

    # API Configuration
    API_URL = "https://api.stlouisfed.org/fred/series/observations"
    API_TIMEOUT = 180
    DEFAULT_SERIES_ID = "SP500"

    # AWS Configuration
    SECRET_ID = "dev/FredExtractor/APIKey"
    SECRET_KEY = "fred-api-key"

    # HTTP Status Codes
    HTTP_OK = 200
    HTTP_NO_CONTENT = 204

    def __init__(
        self,
        event: dict,
        context,
        session: boto3.Session,
        bucket: str,
        series_id: str = DEFAULT_SERIES_ID,
    ) -> None:
        """
        Initialize the FRED data extractor.

        Args:
            event: Lambda event containing execution time
            context: Lambda context object
            session: Boto3 session for AWS service access
            bucket: S3 bucket name for data storage
            series_id: FRED series identifier (default: SP500)

        Raises:
            ValueError: If required event data is missing
        """
        self._validate_event(event)

        self.event = event
        self.context = context
        self.session = session
        self.bucket = bucket
        self.series_id = series_id
        self._observation_date: Optional[pendulum.DateTime] = None
        self._api_key: Optional[str] = None

    @staticmethod
    def _validate_event(event: dict) -> None:
        """Validate that the event contains required fields."""
        if not event or "time" not in event:
            raise ValueError("Event must contain 'time' field")

    @property
    def observation_date(self) -> pendulum.DateTime:
        """
        Lazily compute and cache the observation date from the event.
        The observation date is one day before the event time.

        Returns:
            Observation date as pendulum DateTime
        """
        if self._observation_date is None:
            event_datetime = pendulum.parse(self.event["time"])
            self._observation_date = event_datetime.subtract(days=1)
        return self._observation_date

    def execute(self) -> dict:
        """
        Execute the complete FRED data extraction pipeline.

        Returns:
            Response dictionary with HTTP status code

        Raises:
            Exception: If any step in the pipeline fails
        """
        try:
            logger.info(
                f"[FredExtractor][execute] Starting extraction for series: {self.series_id}, "
                f"observation date: {self.observation_date.to_date_string()}"
            )

            response = pipe(
                self.retrieve_api_key(),
                self.request_fred_data,
                self.store_fred_data_in_s3,
            )

            logger.info("[FredExtractor][execute] Extraction completed successfully")
            return response

        except Exception as e:
            logger.error(f"[FredExtractor][execute] Pipeline failed: {str(e)}", exc_info=True)
            raise

    def request_fred_data(self, api_key: str) -> dict:
        """
        Request data from the FRED API for the specified observation date.

        Args:
            api_key: FRED API key for authentication

        Returns:
            API response as dictionary containing observations

        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If API response is invalid
        """
        logger.info(
            f"[FredExtractor][request_fred_data] Requesting data for {self.series_id} "
            f"on {self.observation_date.to_date_string()}"
        )

        observation_date_string = self.observation_date.format("YYYY-MM-DD")
        params = {
            "series_id": self.series_id,
            "frequency": "d",
            "observation_start": observation_date_string,
            "observation_end": observation_date_string,
            "api_key": api_key,
            "file_type": "json",
        }

        try:
            response = requests.get(
                url=self.API_URL,
                params=params,
                timeout=self.API_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            self._validate_api_response(data)

            logger.info(
                f"[FredExtractor][request_fred_data] Received {len(data.get('observations', []))} observations"
            )
            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f"[FredExtractor][request_fred_data] HTTP error: {e.response.status_code}")
            raise
        except requests.exceptions.Timeout:
            logger.error(f"[FredExtractor][request_fred_data] Request timed out after {self.API_TIMEOUT}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[FredExtractor][request_fred_data] Request failed: {str(e)}")
            raise

    @staticmethod
    def _validate_api_response(data: dict) -> None:
        """
        Validate the structure of the FRED API response.

        Args:
            data: API response dictionary

        Raises:
            ValueError: If response structure is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("API response must be a dictionary")

        if "observations" not in data:
            raise ValueError("API response missing 'observations' field")

        if not isinstance(data["observations"], list):
            raise ValueError("API response 'observations' must be a list")

    def store_fred_data_in_s3(self, api_response: dict) -> dict:
        """
        Store FRED API response data in S3 with partitioned structure.

        Args:
            api_response: FRED API response containing observations

        Returns:
            Dictionary with HTTP status code

        Raises:
            ClientError: If S3 upload fails
        """
        logger.info("[FredExtractor][store_fred_data_in_s3] Processing API response")

        observations = api_response.get("observations", [])

        if len(observations) == 0:
            logger.warning(
                f"[FredExtractor][store_fred_data_in_s3] No data available for "
                f"{self.series_id} on {self.observation_date.to_date_string()}"
            )
            return {"HTTPStatusCode": self.HTTP_NO_CONTENT}

        try:
            client = self.session.client("s3")
            object_key = self.generate_s3_object_key()

            # Convert to JSON with proper formatting
            body = json.dumps(api_response, indent=2, ensure_ascii=False)

            response = client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=body,
                ContentType="application/json",
            )

            logger.info(
                f"[FredExtractor][store_fred_data_in_s3] Successfully saved data to "
                f"s3://{self.bucket}/{object_key}"
            )
            return {"HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"]}

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"[FredExtractor][store_fred_data_in_s3] Failed to upload to S3: {error_code}",
                exc_info=True
            )
            raise

    def retrieve_api_key(self) -> str:
        """
        Retrieve FRED API key from AWS Secrets Manager with caching.

        Returns:
            FRED API key string

        Raises:
            ClientError: If secret retrieval fails
            ValueError: If secret format is invalid
        """
        # Return cached API key if available
        if self._api_key is not None:
            logger.debug("[FredExtractor][retrieve_api_key] Using cached API key")
            return self._api_key

        logger.info(f"[FredExtractor][retrieve_api_key] Retrieving secret: {self.SECRET_ID}")

        try:
            client = self.session.client(service_name="secretsmanager")
            response = client.get_secret_value(SecretId=self.SECRET_ID)

            secret = json.loads(response["SecretString"])

            if self.SECRET_KEY not in secret:
                raise ValueError(
                    f"Secret '{self.SECRET_ID}' missing required key: '{self.SECRET_KEY}'"
                )

            self._api_key = secret[self.SECRET_KEY]
            logger.info("[FredExtractor][retrieve_api_key] Successfully retrieved API key")
            return self._api_key

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"[FredExtractor][retrieve_api_key] Failed to retrieve secret: {error_code}",
                exc_info=True
            )
            raise
        except json.JSONDecodeError as e:
            logger.error(
                f"[FredExtractor][retrieve_api_key] Invalid JSON in secret",
                exc_info=True
            )
            raise ValueError(f"Secret '{self.SECRET_ID}' contains invalid JSON") from e

    def generate_s3_object_key(self) -> str:
        """
        Generate S3 object key with Hive-style partitioning.

        Format: fred/{series_id}/year={YYYY}/month={MM}/{series_id}-{YYYY-MM-DD}.json

        Returns:
            S3 object key string

        Example:
            fred/SP500/year=2026/month=01/SP500-2026-01-24.json
        """
        year = self.observation_date.format("YYYY")
        month = self.observation_date.format("MM")
        date_string = self.observation_date.format("YYYY-MM-DD")

        object_key = (
            f"fred/{self.series_id}/year={year}/month={month}/"
            f"{self.series_id}-{date_string}.json"
        )

        logger.debug(f"[FredExtractor][generate_s3_object_key] Generated key: {object_key}")
        return object_key
