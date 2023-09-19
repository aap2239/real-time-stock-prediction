import streamlit as st
from streamlit.components.v1 import html  # Correct import statement
import requests

def theTweet(tweet_url):
    api = "https://publish.twitter.com/oembed?url={}".format(tweet_url)
    return requests.get(api).json()["html"]

inp = st.text_input("Enter ID of Tweet")
inp = f"https://twitter.com/anyuser/status/{inp}"
if inp:
    res = theTweet(inp)
    html(res, height=700)  # Use the correct function