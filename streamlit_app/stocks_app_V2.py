import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.graph_objs as go
import plotly.express as px
from wordcloud import WordCloud
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time


## Big Query Variables
client = bigquery.Client()
PROJECT_ID = "llsp-project-378023"
DATASET_ID_YFINANCE = "yf_gcs"
DATASET_ID_NEWS = "news_gcs"
DATASET_ID_TWITTER = "twitter_gcs"
TABLE_ID_YFINANCE = "yfdata"
TABLE_ID_TWITTER = "twittertable"
TABLE_ID_NEWS = "newstable"

results = None

## Dictionary to map tickers to Companies 
DICT_OF_COMPANIES = {
    "GOOGL": "Google",
    "AMZN": "Amazon", 
    "MSFT": "Microsoft",
    "TSLA": "Tesla",
    #"META": "Meta",
}

## Utility Functions
def get_bigquery_query(project_id, dataset_id, table_id, company_id=None):
    if company_id is not None:
        return f"SELECT * FROM {project_id}.{dataset_id}.{table_id} WHERE Company = '{company_id}';"
    else:
        return f"SELECT * FROM {project_id}.{dataset_id}.{table_id};"


def run_bigquery_query(query):
    query_job = client.query(query)
    return query_job.result().to_dataframe()


st.set_page_config(
    page_title="Stock Analysis App", page_icon=":chart_with_upwards_trend:"
)
st.set_option("deprecation.showPyplotGlobalUse", False)

def display_stock_line_graph(company):
    stock_data = run_bigquery_query(
        get_bigquery_query(
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID_YFINANCE,
            table_id=TABLE_ID_YFINANCE,
            company_id=company,
        )
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Close"], name="close"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Open"], name="open"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["High"], name="high"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Low"], name="low"))

    fig.update_layout(
        title=f"{company} Stock Prices", xaxis_title="Date", yaxis_title="Price"
    )
    st.plotly_chart(fig)


def display_company_page():

    # Sidebar
    st.sidebar.title("Select a Company")
    companies = DICT_OF_COMPANIES.keys()
    company = st.sidebar.selectbox("Choose a company", companies)

    if company not in companies:
        st.error("Error: Company not found in the data!")
        st.stop()

    st.title(f"{DICT_OF_COMPANIES[company]} Stock Analysis")
    display_stock_line_graph(company)

    # add additional analysis or information as needed
    st.write("Additional analysis or information goes here.")

    # Filter news for the selected company
    filtered_news = run_bigquery_query(get_bigquery_query(PROJECT_ID, DATASET_ID_NEWS, TABLE_ID_NEWS, company))
    # Filter news for the selected company

    company_logos = {
        "META": "https://1000logos.net/wp-content/uploads/2021/10/logo-Meta.png",
        "GOOGL": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "MSFT": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
        "AMZN": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "TSLA": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg",
    }
    # Display company logo
    st.sidebar.image(company_logos[company], use_column_width=True)

    # Main title and background color
    st.title(f"{DICT_OF_COMPANIES[company]} News Dashboard")
    # Define the CSS style
    st.markdown(
        """
        <style>
            body {
                background-color: black;
            }
            .sidebar {
                background-color: white;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
    st.header("Latest News Headlines")
    for index, news in filtered_news.head(10).iterrows():
        sentiment_color = "#FFFFFF"  # default to white for neutral sentiment
        if news["Sentiment"] == "positive":
            sentiment_color = "#00FF00"  # green for positive sentiment
        elif news["Sentiment"] == "negative":
            sentiment_color = "#FF0000"  # red for negative sentiment
        st.write(
            f"<div style='background-color:{sentiment_color}; padding:10px;'>{news['Date']} : {news['News']}</div>",
            unsafe_allow_html=True,
        )

    # Generate word cloud for the selected company
    st.header("Word Cloud")
    text = " ".join(filtered_news["News"].astype(str).tolist())
    wordcloud = WordCloud().generate(text)
    st.image(wordcloud.to_array(), width=500, use_column_width=False)

    # Main title and background color
    st.title(f"{DICT_OF_COMPANIES[company]} Twitter Dashboard")
    
    # Filter data by selected company
    filtered_tweets = run_bigquery_query(get_bigquery_query(PROJECT_ID, DATASET_ID_TWITTER, TABLE_ID_TWITTER, company))

    # Display tweets table
    st.markdown(f"## {DICT_OF_COMPANIES[company]} Tweets")
    st.dataframe(filtered_tweets[["Date", "Text"]])

    # Display sentiment analysis charts
    st.markdown(f"## {company} Sentiment Analysis")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=["Negative"], y=[filtered_tweets["Negative"].mean()], name="Negative")
    )
    fig.add_trace(
        go.Bar(x=["Neutral"], y=[filtered_tweets["Neutral"].mean()], name="Neutral")
    )
    fig.add_trace(
        go.Bar(x=["Positive"], y=[filtered_tweets["Positive"].mean()], name="Positive")
    )
    fig.update_layout(title=f"Sentiment Analysis for {DICT_OF_COMPANIES[company]}")
    st.plotly_chart(fig)

    # Display word cloud with Twitter logo background shape
    st.markdown(f"## {DICT_OF_COMPANIES[company]} Word Cloud")
    # text = " ".join(filtered_tweets["Text"].tolist())
    text = " ".join(filtered_tweets["Text"].astype(str).tolist())

    
    wordcloud = WordCloud(background_color="white").generate(text)
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.margins(x=0, y=0)
    st.pyplot(plt.gcf())  # Pass the current figure to st.pyplot()

    # Hide Streamlit's menu and footer
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


display_company_page()
