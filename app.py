import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import robin_stocks.robinhood as r
from robin_stocks.robinhood import options
import subprocess
from datetime import datetime
from dataclasses import dataclass

# ========== Data Structures ==========

@dataclass
class OptionContract:
    strike: float
    expiration: str
    callPrice: float
    putPrice: float
    volatility: float
    
# ========== Utility Functions ==========

from fetchOptionData import fetchOptionsData, robinhoodLogin
from blackScholes_IV import blackScholesCalculation, impliedVolatilityCalculation, loss

def timeToExpiration(expirationInput):
    '''
        - Takes a date in YYYY-MM-DD format and outputs a singular value for time to maturity/expiration
    '''
    expirationDate = datetime.strptime(expirationInput, "%Y-%m-%d").date()
    today = datetime.today().date()
    daysToExpiration = (expirationDate - today).days
    T = daysToExpiration / 252
    return max(T, 0)

def csvOverwrite():
    '''
        - Clears options data from .csv file
    '''
    with open("options_data.csv", "w") as f:
        f.write("strike,expiration,call_price,put_price,implied_volatility\n")
        
def loadOptionContract(filepath="options_data.csv"):
    df = pd.read_csv(filepath)
    return[
        OptionContract(
            strike = row['strike'],
            expiration = row['expiration'],
            callPrice = row['call_price'],
            putPrice = row['put_price'],
            volatility = row['implied_volatility']
            
        )
        for _, row in df.iterrows
    ]

def blackScholesValues():
    pass
        
# ========== Streamlit UI Functions ==========
def sidebarInputs() -> tuple[str, str, float]:
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
    
    if selectedExpiration:
        try:
            df = pd.read_csv("options_data.csv")
            filtered_df = df[df['expiration'] == selectedExpiration]
            strikes = sorted(filtered_df['strike'].unique().tolist())
            selectedStrikePrice = st.sidebar.selectbox("Strike Price", options=strikes)
        except Exception as e:
            st.sidebar.warning(f"Could not load strike prices: {e}")
            strikes = []
            
    if st.sidebar.button("Fetch Options Data") and selectedExpiration:
        try:
            fetchOptionsData(ticker, selectedExpiration, csv="options_data.csv")
            st.success(f"Fetched {ticker} options data for {selectedExpiration}")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

def displayDataTable(filepath="options_data.csv"):
    try:
        df = pd.read_csv("options_data.csv")
        df = df.rename(columns={
        "strike": "Strike Price",
        "expiration": "Expiration Date",
        "call_price": "Call Price", 
        "put_price": "Put Price",
        "implied_volatility": "Implied Volatility (RH)"
    })
        st.subheader("Options Chain Data")
        st.dataframe(df, use_container_width=True, height=140)
        
    except FileNotFoundError:
        st.warning("Options data not loaded. Please fetch data first.")
        
# ========== Main Application ==========

def main():
    
    robinhoodLogin()
    st.set_page_config(layout="wide")
    sidebarInputs()
    displayDataTable()

    

if __name__ == '__main__':
    main()

    


    
    