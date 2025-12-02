import streamlit as st
import feedparser
import pandas as pd
import requests
import datetime
from dateutil import parser
from supabase import create_client, Client
import os

st.set_page_config(page_title="TT News Agent", layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@st.cache_resource
def supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = supabase_client()

RSS_FEEDS = [
    "https://newsday.co.tt/feed/",
    "https://trinidadexpress.com/search/?f=rss&t=article&l=50&s=start_time&sd=desc&c[]=news*&c[]=local_news*&c[]=editorial*",
    "https://guardian.co.tt/rss/"
]

st.title("🇹🇹 TT News Agent — Prototype (Cloud Version)")

def fetch_feeds():
    rows = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            rows.append({
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published", None),
                "summary": entry.get("summary", "")
            })
    return pd.DataFrame(rows)

st.sidebar.header("Controls")
if st.sidebar.button("Fetch Latest News"):
    df = fetch_feeds()
    st.session_state["articles"] = df

    # Push to Supabase
    for _, r in df.iterrows():
        supabase.table("articles").upsert({
            "title": r["title"],
            "link": r["link"],
            "published": r["published"],
            "summary": r["summary"]
        }).execute()

    st.success("Fetched and stored!")

if "articles" in st.session_state:
    st.subheader("Articles")
    st.dataframe(st.session_state["articles"])
else:
    st.info("Click 'Fetch Latest News' to begin.")

