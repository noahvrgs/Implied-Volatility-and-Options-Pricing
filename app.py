import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import robin_stocks.robinhood as r
from robin_stocks.robinhood import options
import subprocess

from fetchOptionData import fetchOptionsData, robinhoodLogin

# Initial Robinhood Login
robinhoodLogin()

# Sidebar Menu + Logic
st.sidebar.header("Options Pricing Inputs")
ticker = st.sidebar.text_input(label="Stock Ticker", placeholder="e.g. AAPL, TSLA, NVDA")
expirations = []

if ticker:
    try:
        chain = r.options.get_chains(ticker)
        expirations = chain['expiration_dates']
    except Exception as e:
        st.sidebar.warning(f"Could not load expirations: {e}")
           
selectedExpiration = st.sidebar.selectbox("Expiration Date", options=expirations)

# Fetch Options Data Button
if st.sidebar.button("Fetch Options Data") and selectedExpiration:
    try:
        fetchOptionsData(ticker, selectedExpiration, csv="options_data.csv")
        st.success(f"Fetched {ticker} options data for {selectedExpiration}")
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        
if selectedExpiration:
    try:
        df = pd.read_csv("options_data.csv")
        filtered_df = df[df['expiration'] == selectedExpiration]
        strikes = sorted(filtered_df['strike'].unique().tolist())
        selectedStrikePrice = st.sidebar.selectbox("Strike Price", options=strikes)
    except Exception as e:
        st.sidebar.warning(f"Could not load strike prices: {e}")
        strikes = []
        


try:
    df = pd.read_csv("options_data.csv")
    df = df.rename(columns={
    "strike": "Strike Price",
    "expiration": "Expiration Date",
    "call_price": "Call Price",
    "put_price": "Put Price",
    "implied_volatility": "Implied Volatility"
})
    st.dataframe(df, use_container_width=True, height=200)
    
except FileNotFoundError:
    st.warning("Options data not loaded. Please fetch data first.")
    

    
    
    