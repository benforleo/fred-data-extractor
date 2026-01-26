import logging
import os
from typing import Any

import boto3

from fred_extractor.fred_extractor import FredExtractor

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FRED_BUCKET_NAME = os.getenv("FRED_BUCKET_NAME")
FRED_SERIES_ID = os.getenv("FRED_SERIES_ID", "SP500")


session = boto3.Session()


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler for FRED data extraction."""

    if not FRED_BUCKET_NAME:
        raise ValueError("FRED_BUCKET_NAME environment variable is not set")

    try:
        fred = FredExtractor(event, context, session, bucket=FRED_BUCKET_NAME, series_id=FRED_SERIES_ID)
        response = fred.execute()
        logger.info("Successfully executed FRED extraction")
        return response

    except Exception as err:
        logger.error(f"Error during FRED extraction: {err}")
        raise err
