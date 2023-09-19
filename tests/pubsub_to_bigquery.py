import os
import json

from google.cloud import pubsub_v1
from google.cloud import bigquery

# Set your Google Cloud project ID as an environment variable
project_id = "llsp-project-378023"

# Replace with your desired Pub/Sub topic and subscription names
topic_name = "polygon-data"
subscription_name = "polygon-data-sub"

# Replace with your desired BigQuery dataset and table names
dataset_name = "polygon_data_dataset"
table_name = "polygon_data_table"

# Initialize a Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

# Initialize a BigQuery client
bigquery_client = bigquery.Client(project=project_id)

# Create the dataset and table if they do not exist
dataset_ref = bigquery_client.dataset(dataset_name)
table_ref = dataset_ref.table(table_name)

if not bigquery_client.get_dataset(dataset_ref):
    bigquery_client.create_dataset(bigquery.Dataset(dataset_ref))

if not bigquery_client.get_table(table_ref):
    schema = [
        bigquery.SchemaField("open", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("high", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("low", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("close", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("volume", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("vwap", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("transactions", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("otc", "BOOLEAN", mode="NULLABLE"),
    ]
    table = bigquery.Table(table_ref, schema=schema)
    bigquery_client.create_table(table)

# Define the callback function for processing received messages
def process_message(message):
    print(f"Received message: {message.data}")

    # Deserialize the message data and insert it into the BigQuery table
    data = json.loads(message.data)
    rows_to_insert = [data]
    errors = bigquery_client.insert_rows_json(table_ref, rows_to_insert)

    if not errors:
        print("Inserted rows successfully.")
        message.ack()
    else:
        print(f"Failed to insert rows: {errors}")


# Subscribe to the Pub/Sub topic and process messages
streaming_pull_future = subscriber.subscribe(
    subscription_path, callback=process_message
)
print(f"Listening for messages on {subscription_path}...")

# Keep the script running indefinitely
try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
