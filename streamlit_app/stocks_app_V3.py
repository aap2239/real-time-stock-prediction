# Import necessary libraries
import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time 
import requests
from streamlit.components.v1 import html

# Initialize BigQuery client
client = bigquery.Client()

# Set up project and dataset IDs
PROJECT_ID = "llsp-project-378023"
TABLE_ID_YFINANCE = "yf_gcs.yfdata"
TABLE_ID_TWITTER = "twitter_gcs.twittertable"
TABLE_ID_NEWS = "news_gcs.newstable"

# Dictionary to map tickers to Companies
DICT_OF_COMPANIES = {
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "MSFT": "Microsoft",
    "TSLA": "Tesla",
}

# Utility Functions
def get_required_table(
        project_id: str,
        table_id: str,
        company_id: str = None,
):
    if company_id is None:
        return client.query(f"SELECT * FROM `{project_id}.{table_id}`;").result().to_dataframe()

    else:
        return client.query(f"SELECT * FROM `{project_id}.{table_id}` WHERE Company = '{company_id}';").result().to_dataframe()
    
def theTweet(tweet_url):
    api = "https://publish.twitter.com/oembed?url={}".format(tweet_url)
    return requests.get(api).json()["html"]

def rotate(lst, n):
    return lst[-n:] + lst[:-n]


def create_radar_chart(tweet, start_angle=45):
    sentiment_labels = ["Negative", "Neutral", "Positive"]
    sentiment_values = [tweet["Negative"], tweet["Neutral"], tweet["Positive"]]

    angle_step = 360 // len(sentiment_labels)
    rotation_steps = start_angle // angle_step

    rotated_labels = rotate(sentiment_labels, rotation_steps)
    rotated_values = rotate(sentiment_values, rotation_steps)

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=rotated_values,
            theta=rotated_labels,
            fill="toself",
            name="Sentiment",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False
    )

    return fig

## stocks plot function
def display_stock_line_graph(company):
    st.title(f"{DICT_OF_COMPANIES[company]} Stocks Dashboard")
    stock_data = get_required_table(PROJECT_ID, TABLE_ID_YFINANCE, company)
    stock_data.sort_values(by='Date')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Close"], name="close"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Open"], name="open"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["High"], name="high"))
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Low"], name="low"))

    fig.update_layout(
        title=f"{company} Stock Prices", xaxis_title="Date", yaxis_title="Price"
    )
    st.plotly_chart(fig)
## Display News
# Display company log

def display_news(company):
    news_data = get_required_table(PROJECT_ID, TABLE_ID_NEWS, company)
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
    for index, news in news_data.head(10).iterrows():
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
    text = " ".join(news_data["News"].astype(str).tolist())
    wordcloud = WordCloud().generate(text)
    st.image(wordcloud.to_array(), width=500, use_column_width=False)

## twitter plotting function
def display_tweets(company):
    st.title(f"{DICT_OF_COMPANIES[company]} Twitter Dashboard")
    tweet_data = get_required_table(PROJECT_ID, TABLE_ID_TWITTER, company)
    tweet_container = st.empty()
    chart_container = st.empty()
    while True:
        for index, tweet in tweet_data.iterrows():
            tweet_container.write(f"{tweet['Date']} - {tweet['Text']}")
            res = theTweet(f"https://twitter.com/anyuser/status/{tweet['Id']}")
            #tweet_container.write(html(res, height=700))
            radar_chart = create_radar_chart(tweet)
            chart_container.plotly_chart(radar_chart)
            time.sleep(5)
            tweet_container.empty()
            chart_container.empty()

def main():
    # Set up page configuration
    st.set_page_config(
        page_title="Stock Analysis App",
        page_icon=":chart_with_upwards_trend:",
    )

    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    pages = ["Home", "Company Analysis"]
    selected_page = st.sidebar.radio("Go to", pages)

    if selected_page == "Home":
        st.title("Welcome to the Stock Analysis App!")
        st.subheader("Analyze stock data using various visualizations and insights")
        
        st.write(
            """
            This app allows you to analyze stock data for different companies. Navigate to the "Company Analysis" 
            page using the sidebar to start exploring stock data.
            
            Features of this app include:
            
            - Line graphs displaying stock prices over time
            - Sentiment analysis based on news articles and tweets
            - Word clouds highlighting key terms and trends
            
            The data used in this app is sourced from various public APIs and databases, including Yahoo Finance, 
            Twitter, and news articles.
            
            Happy analyzing!
            """
        )

    elif selected_page == "Company Analysis":
        st.sidebar.title("Select a Company")
        
        # You can add your stock analysis code here for the selected company
        companies = DICT_OF_COMPANIES.keys()
        company = st.sidebar.selectbox("Choose a Company", companies)
        #st.title(f"{companies[company]} Stock Analysis")
        display_stock_line_graph(company)
        display_news(company)
        display_tweets(company)

if __name__ == "__main__":
    main()