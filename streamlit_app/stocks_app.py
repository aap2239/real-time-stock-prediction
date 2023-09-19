import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Function to fetch historical stock data
def get_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


# Function to load tweets from CSV file
@st.cache_resource(ttl=60)  # Set cache time-to-live to 60 seconds (1 minute)
def load_tweets(csv_file):
    print("loaded new data")
    return pd.read_csv(csv_file)


# Sidebar
st.sidebar.title("Select a Company")
company = st.sidebar.selectbox("Choose a company", ("Apple", "Google", "Microsoft"))

# Map company names to their ticker symbols
ticker_map = {"Apple": "AAPL", "Google": "GOOGL", "Microsoft": "MSFT"}

# Get the historical stock data
start_date = "2020-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")
stock_data = get_stock_data(ticker_map[company], start_date, end_date)

# Main title
st.title(f"{company} Stock Market Trends")

# Display historical stock prices timeseries line chart
st.header("Historical Stock Prices")
fig = px.line(
    stock_data, x=stock_data.index, y="Close", labels={"x": "Date", "y": "Close Price"}
)
st.plotly_chart(fig)

# Load and display live tweets
st.header("Live Tweets")
tweets_csv = "data/datafiles_twdata (2).csv"
tweets_df = load_tweets(tweets_csv)

# Filter tweets for the selected company
filtered_tweets = tweets_df[tweets_df["Stocks"] == company]


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


# Display one tweet at a time with a sleep timer of 5 seconds
tweet_container = st.empty()
chart_container = st.empty()

while True:
    for index, tweet in filtered_tweets.iterrows():
        tweet_container.write(f"{tweet['Date']} - {tweet['Tweet']}")
        radar_chart = create_radar_chart(tweet)
        chart_container.plotly_chart(radar_chart)
        time.sleep(5)
        tweet_container.empty()
        chart_container.empty()
