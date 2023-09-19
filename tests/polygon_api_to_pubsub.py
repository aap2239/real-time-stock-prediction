import os
import json
import time
import requests

from google.cloud import pubsub_v1
from google.cloud import bigquery

from polygon import RESTClient
from datetime import datetime, timedelta


def agg_to_dict(bar) -> dict:
    return {
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "vwap": bar.vwap,
        "timestamp": str(datetime.fromtimestamp(bar.timestamp / 1000)),
        "transactions": bar.transactions,
        "otc": bar.otc,
    }


def fetch_polygon_data_and_publish(from_="2023-01-09", to_="2023-01-10"):
    # Fetch data from the Polygon API
    bars = client.get_aggs(
        ticker=ticker,
        multiplier=1,
        timespan="hour",
        from_=from_,
        to=to_,
    )
    # print(bars)
    for bar in bars:
        print(bar)
        message = agg_to_dict(bar)
        message = json.dumps(message)
        future = publisher.publish(topic_path, message.encode("utf-8"))
        print(f"Published message: {message}")


# Set your Polygon API key and Google Cloud project ID as environment variables
polygon_api_key = "vxN2609Np1VMLG7ie7BYPKAHfsijG_tB"
project_id = "llsp-project-378023"
client = RESTClient(api_key=polygon_api_key)


# Replace with your desired Pub/Sub topic name
topic_name = "polygon-data"
ticker = "X:BTCUSD"
# Initialize a Pub/Sub publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

if __name__ == "__main__":
    from_ = "2023-01-09"
    to_ = "2023-01-10"
    while True:
        print("From: ", from_)
        print("To: ", to_)

        fetch_polygon_data_and_publish(
            from_=from_,
            to_=to_,
        )
        date_object = datetime.strptime(to_, "%Y-%m-%d").date()
        # Add one day to the date object
        next_day = date_object + timedelta(days=1)
        # Convert the date object back to a string
        from_ = to_
        to_ = next_day.strftime("%Y-%m-%d")

        time.sleep(20)
