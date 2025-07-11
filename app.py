import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import robin_stocks.robinhood as r
from robin_stocks.robinhood import options
import subprocess

from fetchOptionData import fetchOptionsData, robinhoodLogin
from blackScholes_IV import blackScholesCalculation, impliedVolatilityCalculation, loss

# Initial Robinhood Login & CSV wiped clean
robinhoodLogin()

# with open("options_data.csv", "w") as f:
#     f.write("strike,expiration,call_price,put_price,implied_volatility\n")


#--------------------------------------------------------------------------------------------
# Sidebar Menu + Logic
st.sidebar.header("Options Pricing Inputs")
# st.sidebar.write("Created by:")
# linkedin_url = "https://www.linkedin.com/in/noah-vargas-b04a15290/"
# st.sidebar.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Noah Vargas`</a>', unsafe_allow_html=True)
ticker = st.sidebar.text_input(label="Stock Ticker", placeholder="e.g. AAPL, TSLA, NVDA")
expirations = []

# Expiration Date Dropdown When Ticker Selected
if ticker:
    try:
        chain = r.options.get_chains(ticker)
        expirations = chain['expiration_dates']
    except Exception as e:
        st.sidebar.warning(f"Could not load expirations: {e}")
           
selectedExpiration = st.sidebar.selectbox("Expiration Date", options=expirations)


# Strike Prices Dropdown When Selected Expiration (Sidebar)   
if selectedExpiration:
    try:
        df = pd.read_csv("options_data.csv")
        filtered_df = df[df['expiration'] == selectedExpiration]
        strikes = sorted(filtered_df['strike'].unique().tolist())
        selectedStrikePrice = st.sidebar.selectbox("Strike Price", options=strikes)
    except Exception as e:
        st.sidebar.warning(f"Could not load strike prices: {e}")
        strikes = []
        
        
if selectedStrikePrice:
    
        
        
# Fetch Options Data Button
if st.sidebar.button("Fetch Options Data") and selectedExpiration:
    try:
        fetchOptionsData(ticker, selectedExpiration, csv="options_data.csv")
        st.success(f"Fetched {ticker} options data for {selectedExpiration}")
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")

#----------------------------------------------------------------------------------------------


st.set_page_config(layout="wide")    

# Graph & Share Price
st.header(ticker)

# Table + Header Rename
try:
    df = pd.read_csv("options_data.csv")
    df = df.rename(columns={
    "strike": "Strike Price",
    "expiration": "Expiration Date",
    "call_price": "Call Price",
    "put_price": "Put Price",
    "implied_volatility": "Implied Volatility (RH)"
})
    st.dataframe(df, use_container_width=True, height=140)
    
except FileNotFoundError:
    st.warning("Options data not loaded. Please fetch data first.")
    

    
    
    