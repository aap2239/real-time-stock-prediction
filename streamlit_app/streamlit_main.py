# Import necessary libraries
import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time 
import requests
from textblob import TextBlob
from streamlit.components.v1 import html
import os 
import altair as alt
import numpy as np


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"constant-setup-383721-b45fde8fb18d.json"
# Initialize BigQuery client
client = bigquery.Client()

# Set up project and dataset IDs
PROJECT_ID = "constant-setup-383721"
TABLE_ID_YFINANCE = "lssp_project.yf_table"
TABLE_ID_MA = "lssp_project.MA"
TABLE_ID_TWITTER = "lssp_project.twitter_table"
TABLE_ID_NEWS = "lssp_project.finviz_table"

# Dictionary to map tickers to Companies
DICT_OF_COMPANIES = {
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "MSFT": "Microsoft",
    "TSLA": "Tesla",
    "META": "Meta",
    "UBER": "Uber",
    "NFLX": "Netflix",
    "AAPL": "Apple"
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


def display_stock_line(company):
    st.title(f"{DICT_OF_COMPANIES[company]} Stock Dashboard")
    st.write("### General Stock Line Graph")    
    # Load data for the selected company
    stock_data = get_required_table(PROJECT_ID, TABLE_ID_YFINANCE, company)
    
    # Check that stock_data is not empty and "Date" column contains at least one non-null value
    if stock_data.empty or stock_data["Date"].isna().all():
        st.warning("No data available for the selected company.")
        return
    
    # Allow user to select date range
    sorted_dates = sorted(stock_data["Date"].unique(), reverse=True)
    date_range = st.multiselect("Select dates", sorted_dates)
    if date_range:
        start_date, end_date = date_range[0], date_range[-1]
        selected_data = stock_data[(stock_data["Date"] >= start_date) & (stock_data["Date"] <= end_date)]
        st.write("### Selected Data")
        # Sort selected_data in reverse order by the "Date" column
        selected_data = selected_data.sort_values(by="Date", ascending=False)
        st.dataframe(selected_data)
    else:
        selected_data = stock_data
        # Sort selected_data in reverse order by the "Date" column
        selected_data = selected_data.sort_values(by="Date", ascending=False)
        st.dataframe(selected_data)
    
    # Create dropdown to select attribute to plot
    attribute = st.selectbox("Select attribute to plot", ["Open", "High", "Low", "Close", "AdjClose", "Volume"])

    # Define a dictionary to map attributes to unique colors
    color_dict = {
        "Open": "#1f77b4",
        "High": "#ff7f0e",
        "Low": "#2ca02c",
        "Close": "#d62728",
        "AdjClose": "#9467bd",
        "Volume": "#8c564b"
    }

    # Create line chart
    chart = alt.Chart(selected_data).mark_line().encode(
        x='Date:T',
        y=attribute + ':Q',
        color=alt.value(color_dict[attribute])
    ).properties(
        width=800,
        height=400
    )

    # Get the latest data point
    latest_data_point = selected_data.iloc[0]
    latest_attribute_value = latest_data_point[attribute]

    # Determine if the stock is rising or dropping based on the latest data point
    if latest_attribute_value > selected_data[attribute].mean():
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is higher than the {attribute} mean. The stock is rising. :chart_with_upwards_trend:")
    elif latest_attribute_value < selected_data[attribute].mean():
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is lower than the {attribute} mean. The stock is dropping.:chart_with_downwards_trend:")
    else:
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is equal to the {attribute} mean. The stock is stable. :yellow_circle:")

        # Display chart
    st.altair_chart(chart, use_container_width=True)

def display_stock_line_ma(company):
    st.write("### 15-Day Moving Average Line Graphs")
    # Load data for the selected company
    stock_data = get_required_table(PROJECT_ID, TABLE_ID_MA, company)
    
    # Check that stock_data is not empty and "Date" column contains at least one non-null value
    if stock_data.empty or stock_data["Date"].isna().all():
        st.warning("No data available for the selected company.")
        return
    
    # Allow user to select date range
    sorted_date = sorted(stock_data["Date"].unique(), reverse=True)
    date_range = st.multiselect("Select date", sorted_date)
    if date_range:
        start_date, end_date = date_range[0], date_range[-1]
        selected_data = stock_data[(stock_data["Date"] >= start_date) & (stock_data["Date"] <= end_date)]
        st.write("### Selected Data")
        # Sort selected_data in reverse order by the "Date" column
        selected_data = selected_data.sort_values(by="Date", ascending=False)
        st.dataframe(selected_data)
    else:
        selected_data = stock_data
        # Sort selected_data in reverse order by the "Date" column
        selected_data = selected_data.sort_values(by="Date", ascending=False)
        st.dataframe(selected_data)
    
    # Create dropdown to select attribute to plot
    attribute = st.selectbox("Select attribute to plot moving average", ["Open", "High", "Low", "Close", "AdjClose", "Volume"], key="attribute_selectbox")

    # Define a dictionary to map attributes to unique colors
    color_dict = {
        "Open": "#1f77b4",
        "High": "#ff7f0e",
        "Low": "#2ca02c",
        "Close": "#d62728",
        "AdjClose": "#9467bd",
        "Volume": "#8c564b"
    }

    # Create line chart
    chart = alt.Chart(selected_data).mark_line().encode(
        x='Date:T',
        y=attribute + ':Q',
        color=alt.value(color_dict[attribute])
    ).properties(
        width=800,
        height=400
    )

    # Get the latest data point
    latest_data_point = selected_data.iloc[0]
    latest_attribute_value = latest_data_point[attribute]

    # Determine if the stock is rising or dropping based on the latest data point
    if latest_attribute_value > selected_data[attribute].mean():
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is higher than the {attribute} mean. The stock is rising. :chart_with_upwards_trend:")
    elif latest_attribute_value < selected_data[attribute].mean():
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is lower than the {attribute} mean. The stock is dropping. :chart_with_downwards_trend:")
    else:
        st.write(f"### {attribute} Analysis")
        st.write(f"The {attribute} value of the latest data point is equal to the {attribute} mean. The stock is stable. :yellow_circle:")

    # Display chart
    st.altair_chart(chart, use_container_width=True)

## Display News
# Display company log

    company_logos = {
    "AAPL": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
    "GOOGL": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
    "MSFT": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
    "AMZN": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "TSLA": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg",
    "UBER": "https://1000logos.net/wp-content/uploads/2017/09/Uber-logo.jpg",
    "META": "https://static.dezeen.com/uploads/2021/11/meta-facebook-rebranding-name-news_dezeen_2364_col_hero2-1024x441.jpg",
    "NFLX": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg"

}

    # Display company logo
    st.sidebar.image(company_logos[company], use_column_width=True)


def display_news(company):
    news_data = get_required_table(PROJECT_ID, TABLE_ID_NEWS, company)
    st.title(f"{DICT_OF_COMPANIES[company]} News Dashboard")

    st.header("Latest News Headlines")
    top_news = news_data[["Date", "News"]].head(5).reset_index(drop=True)
    for index, news in top_news.iterrows():
        st.write(f"{news['Date']} : {news['News']}")


def display_charts_news(company):

    news_data = get_required_table(PROJECT_ID, TABLE_ID_NEWS, company)
    st.header("Overall News Sentiment")
    #st.write(len(news_data))
    # Perform sentiment analysis on the news data
    sentiment_counts = news_data["News"].apply(lambda x: TextBlob(x).sentiment.polarity)\
        .apply(lambda x: "positive" if x > 0.0 else "negative" if x < 0.0 else "neutral").value_counts(normalize=True) * 100
    
    # Plot the sentiment analysis results
    fig = go.Figure([go.Bar(x=sentiment_counts.index, y=sentiment_counts.values, marker_color=['#4CAF50', '#FFEB3B', '#FF5722'])])
    fig.update_layout( xaxis_title="Sentiment", yaxis_title="Percentage")
    for i, v in enumerate(sentiment_counts.values):
        fig.add_annotation(x=sentiment_counts.index[i], y=v,
                                text=f"{v:.2f}%",
                                font=dict(size=12, color='white'),
                                showarrow=False,
                                yshift=10)
    
    chart_container = st.empty()
    chart_container.plotly_chart(fig)

    # Generate word cloud for the selected company
    st.header("Overall News Word Cloud")
    text = " ".join(news_data["News"].astype(str).tolist())
    wordcloud = WordCloud().generate(text)
    st.image(wordcloud.to_array(), width=500, use_column_width=False)

def display_charts_twitter(company):

    st.title(f"{DICT_OF_COMPANIES[company]} Twitter Dashboard")
    tweet_data = get_required_table(PROJECT_ID, TABLE_ID_TWITTER, company)
    sentiment_counts = tweet_data["Compound"].apply(lambda x: "positive" if x > 0.05 else "negative" if x < -0.05 else "neutral").value_counts(normalize=True) * 100
    st.header("Overall Twitter Sentiment")
    fig = go.Figure([go.Bar(x=sentiment_counts.index, y=sentiment_counts.values, 
            marker_color=['#FFEB3B', '#4CAF50', '#FF5722'])])


    fig.update_layout( xaxis_title="Sentiment", yaxis_title="Percentage")
    for i, v in enumerate(sentiment_counts.values):
        fig.add_annotation(x=sentiment_counts.index[i], y=v,
                                text=f"{v:.2f}%",
                                font=dict(size=12, color='white'),
                                showarrow=False,
                                yshift=10)
    chart_container = st.empty()
    chart_container.plotly_chart(fig)

    # Generate word cloud for the selected company
    st.header("Overall Twitter Word Cloud")
    text = " ".join(tweet_data["Text"].astype(str).tolist())
    wordcloud = WordCloud(background_color='black', colormap='Set2', collocations=False).generate(text)
    st.image(wordcloud.to_array(), width=500, use_column_width=False)

def display_tweets(company):
    st.header("Dynamic display of most recent tweets and their sentiment")
    tweet_data = get_required_table(PROJECT_ID, TABLE_ID_TWITTER, company)
    tweet_container = st.empty()
    chart_container = st.empty()
    colors = [ '#FF5722', '#FFEB3B','#4CAF50']
    for index, tweet in tweet_data.iterrows():
        tweet_container.write(f"{tweet['Date']} - {tweet['Text']}")
        negative = tweet['Negative']
        neutral = tweet['Neutral']
        positive = tweet['Positive']
        sentiment_counts = pd.Series([negative, neutral, positive], index=["Negative", "Neutral", "Positive"])
        fig = go.Figure(data=[go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, 
                            marker=dict(colors=colors))])
        chart_container.plotly_chart(fig, use_container_width=True)
        time.sleep(2)
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
        
        # Add an image related to the stock market
        st.image("https://media.istockphoto.com/id/913219882/photo/financial-graph-on-technology-abstract-background.jpg?s=612x612&w=0&k=20&c=0P0vbPiPsHOH_uzZEzL6CmpZwIDIArtNj_PsQVwxkEM=", use_column_width=True)
        
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
        display_stock_line(company)
        display_stock_line_ma(company)
        #display_news(company)
        display_news(company)
        display_charts_news(company)
        display_charts_twitter(company)
        display_tweets(company)


if __name__ == "__main__":
    main()
