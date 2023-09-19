import streamlit as st

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
        
        The data used in this app is sourced from various public APIs and databases, including Google Finance, 
        Twitter, and news articles.
        
        Happy analyzing!
        """
    )

elif selected_page == "Company Analysis":
    st.sidebar.title("Select a Company")
    companies = {
        "GOOGL": "Google",
        "AMZN": "Amazon",
        "MSFT": "Microsoft",
        "TSLA": "Tesla",
    }
    company = st.sidebar.selectbox("Choose a company", list(companies.keys()))

    st.title(f"{companies[company]} Stock Analysis")
    
    # You can add your stock analysis code here for the selected company
    st.write(f"Stock analysis content for {companies[company]} will be displayed here.")