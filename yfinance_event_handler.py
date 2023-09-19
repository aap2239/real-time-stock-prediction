from flask import jsonify
from google.cloud import storage
from pandas_datareader import data as pdr
from datetime import date
import pandas as pd
import pandas as pd
import requests
import re
from google.cloud import bigquery
from google.cloud import storage
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")  # download the VADER lexicon
nltk.download("stopwords")  # download the stopwords
nltk.download("punkt")
nltk.download("words")  # Download the English words corpus if not already downloaded
from nltk.corpus import words as english_words

storage_client = storage.Client(project="constant-setup-383721")


def upload_blob(bucket_name, source_data, destination_blob_name):

    """Uploads a file to the bucket. https://cloud.google.com/storage/docs/"""
    print("function upload_blob called")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(source_data.to_csv(index=False, header=False), "text/csv")
    print("File {} uploaded to {}.".format(destination_blob_name, bucket_name))


def event_handler(request):
    queries = ["google stock", "apple stock", "meta stock"]
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAJyaiAEAAAAAaNqO6zh6dxIRAvAGj7STlmm8crQ%3DwqDbQOqfzwFgonTEFnzhlOl4R6PP1t5n1xqmyJyLdudpVA9MpU"

    # Set up the request parameters
    max_results = 100
    headers = {"Authorization": f"Bearer {bearer_token}"}
    queries = ["google stock", "apple stock", "meta stock"]

    stop_words = stopwords.words("english")  # get the list of English stopwords
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE,
    )
    url_pattern = re.compile(r"http\S+")  # compile regex pattern for URLs
    data = []
    sia = SentimentIntensityAnalyzer()

    for query in queries:
        url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results={max_results}&tweet.fields=created_at"
        # Send the request to the Twitter API
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Request failed with error {response.status_code}, {response.text}"
            )
        json_response = response.json()

        # Extract relevant information from the response and store in a Pandas dataframe
        for tweet in json_response["data"]:
            text = tweet["text"]
            # Remove URLs from text
            text = re.sub(url_pattern, "", text)

            # Remove emoticons from text
            text = emoji_pattern.sub(r"", text)

            # Remove stopwords from text
            text_tokens = nltk.word_tokenize(text.lower())
            filtered_words = [word for word in text_tokens if word not in stop_words]
            text = " ".join(filtered_words)
            english_words_set = set(
                english_words.words()
            )  # Create a set of English words
            text = " ".join(
                word for word in text.split() if word.lower() in english_words_set
            )

            sentiment_scores = sia.polarity_scores(text)
            created_at = tweet["created_at"]
            created_date = created_at[:10]
            data.append(
                [
                    query,
                    tweet["id"],
                    created_date,
                    text,
                    sentiment_scores["neg"],
                    sentiment_scores["neu"],
                    sentiment_scores["pos"],
                    sentiment_scores["compound"],
                ]
            )
    df = pd.DataFrame(
        data,
        columns=["query", "id", "created_at", "text", "neg", "neu", "pos", "compound"],
    )

    # Transform the dataframe as needed
    # df["text"] = df["text"].str.replace("\n", "")
    # df["pos"] = df["pos"].astype(str)
    # df["neg"] = df["neg"].astype(str)
    # df["neu"] = df["neu"].astype(str)
    # df["compound"] = df["compound"].astype(str)
    file_name = "datafiles/twdata.txt"
    bucket_name = "twitter_cf_to_gcs"
    upload_blob(bucket_name, df, file_name)
