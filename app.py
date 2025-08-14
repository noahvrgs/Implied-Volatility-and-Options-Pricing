# === Import Libraries ===
import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
from datetime import datetime
import seaborn as sns
import robin_stocks.robinhood as r
from robin_stocks.robinhood import options

# ========== Utility/Calculation Function Imports==========
from util import robinhoodLogin, fetchOptionsData

# === Streamlit UI & CSS Functions ===
def cssInjection():
    st.markdown("""
    <style>
    /* Adjust the size and alignment of the CALL and PUT value containers */
    .metric-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px; /* Adjust the padding to control height */
        width: auto; /* Auto width for responsiveness, or set a fixed width if necessary */
        margin: 0 auto; /* Center the container */
    }

    /* Custom classes for CALL and PUT values */
    .metric-call {
        background-color: #90ee90; /* Light green background */
        color: black; /* Black font color */
        margin-right: 10px; /* Spacing between CALL and PUT */
        border-radius: 10px; /* Rounded corners */
    }

    .metric-put {
        background-color: #ffcccb; /* Light red background */
        color: black; /* Black font color */
        border-radius: 10px; /* Rounded corners */
    }

    /* Style for the value text */
    .metric-value {
        font-size: 1.5rem; /* Adjust font size */
        font-weight: bold;
        margin: 0; /* Remove default margins */
    }

    /* Style for the label text */
    .metric-label {
        font-size: 1rem; /* Adjust font size */
        margin-bottom: 4px; /* Spacing between label and value */
    }

    </style>
    """, unsafe_allow_html=True)
    
def optionsTable(optionsContracts):
    columns = [
        "Ticker", "Strike Price", "Expiration", "Time To Maturity",
        "Call Price", "Put Price", "Bid", "Ask", "Implied Volatility (Robinhood)"
    ]
    if optionsContracts:
        inputData = [
            {
                "Ticker": c.ticker,
                "Strike Price": c.strikePrice,
                "Expiration": c.expiration,
                "Time To Maturity": c.timeToMaturity,
                "Call Price": c.callPrice,
                "Put Price": c.putPrice,
                "Bid": c.bidPrice,
                "Ask": c.askPrice,
                "Implied Volatility (Robinhood)": c.volatilityRobinhood
            }
            for c in optionsContracts
        ]
    else:
        inputData = [
            {
                "Ticker": "",
                "Strike Price": "",
                "Expiration": "",
                "Time To Maturity": "",
                "Call Price": "",
                "Put Price": "",
                "Bid": "",
                "Ask": "",
                "Implied Volatility (Robinhood)": ""
            }
        ]
        
    df = pd.DataFrame(inputData, columns=columns)
    st.dataframe(df, use_container_width=True, height=200)

def selectedOption(contract: object, sigmaGuess: float):
    
    def jaxFloat_to_pyFloat(val):
        try:
            return float(val) if val is not None else None
        except:
            return None
        
    try:
        sharePrice = contract.getSharePrice(contract.ticker)
    except:
        pass
        
    try:
        contract.volatilityCallValue = contract.impliedVolatilityCalculation(sharePrice, sigmaGuess, "call")
        contract.volatilityPutValue = contract.impliedVolatilityCalculation(sharePrice, sigmaGuess, "put")
        contract.blackScholesCallValue = contract.blackScholesCalculation(sharePrice, contract.volatilityCallValue, "call")
        contract.blackScholesPutValue = contract.blackScholesCalculation(sharePrice, contract.volatilityPutValue, "put")
    except Exception as e:
        print(f"Could not calculate IV or Black-Scholes: {e}")
    

    inputData = {
        "Current Asset/Share Price": [sharePrice],
        "Strike Price": [contract.strikePrice],
        "Time to Maturity": [contract.timeToMaturity],
        "Calculated Implied Volatility (Call)": [jaxFloat_to_pyFloat(contract.volatilityCallValue)],
        "Calculated Implied Volatility (Put)": [jaxFloat_to_pyFloat(contract.volatilityPutValue)],
        "Risk-Free Interest Rate": [contract.riskFreeRate]
    }

    df = pd.DataFrame(inputData)
    st.dataframe(df, use_container_width=True, height=70)
    
    inputData2 = {
        "Robinhood Call Price": [contract.callPrice],
        "Robinhood Put Price": [contract.putPrice],
        "Black-Scholes Call Price": [jaxFloat_to_pyFloat(contract.blackScholesCallValue)],
        "Black-Scholes Put Price": [jaxFloat_to_pyFloat(contract.blackScholesPutValue)]
    }
    
    df2 = pd.DataFrame(inputData2)
    st.dataframe(df2, use_container_width=True)
    
    # col1, col2 = st.columns([1,1], gap="small")

    # with col1:
    #     # Using the custom class for CALL value
    #     st.markdown(f"""
    #         <div class="metric-container metric-call">
    #             <div>
    #                 <div class="metric-label">Black-Scholes Call Value</div>
    #                 <div class="metric-value">${jaxFloat_to_pyFloat(contract.blackScholesCallValue):.2f}</div>
    #             </div>
    #         </div>
    #     """, unsafe_allow_html=True)

    # with col2:
    #     # Using the custom class for PUT value
    #     st.markdown(f"""
    #         <div class="metric-container metric-put">
    #             <div>
    #                 <div class="metric-label">Black-Scholes Put Value</div>
    #                 <div class="metric-value">${jaxFloat_to_pyFloat(contract.blackScholesPutValue):.2f}</div>
    #             </div>
    #         </div>
    #     """, unsafe_allow_html=True)

def plotHeatmaps(contract: object, spotRange: np.ndarray, volRange: np.ndarray):
    callPrices = np.zeros((len(volRange), len(spotRange)))
    putPrices = np.zeros((len(volRange), len(spotRange)))
    
    for i, vol in enumerate(volRange):
        for j, spot in enumerate(spotRange):
            try:
                callPrice = contract.blackScholesCalculation(spot, vol, "call")
                putPrice = contract.blackScholesCalculation(spot, vol, "put")
            except:
                callPrice, putPrice = np.nan, np.nan
            
            callPrices[i, j] = callPrice
            putPrices[i, j] = putPrice
    
    figCall, axCall = plt.subplots(figsize=(8, 6))
    sns.heatmap(callPrices,
                xticklabels=np.round(spotRange, 2),
                yticklabels=np.round(volRange, 2),
                annot=True,
                fmt=".2f",
                cmap="viridis",
                ax=axCall
                )
    axCall.set_title(f"Call Price Heatmap (Strike = {contract.strikePrice})")
    axCall.set_xlabel("Spot Price")
    axCall.set_ylabel("Volatility")
    
    figPut, axPut = plt.subplots(figsize=(8, 6))
    sns.heatmap(putPrices,
                xticklabels=np.round(spotRange, 2),
                yticklabels=np.round(volRange, 2),
                annot=True,
                fmt=".2f",
                cmap="viridis",
                ax=axPut
                )
    
    axPut.set_title(f"Put Price Heatmap (Strike = {contract.strikePrice})")
    axPut.set_xlabel("Spot Price")
    axPut.set_ylabel("Volatility")

    return figCall, figPut

# === Main Streamlit Application ===
robinhoodLogin()
    
st.set_page_config(
    layout="wide",
    page_title="Implied Volatility & Black-Scholes Option Pricing",
    page_icon="📈",
    initial_sidebar_state="expanded")

cssInjection()

st.header("Implied Volatility & Black-Scholes Option Pricing")
st.info("ℹ️ Below is a video on how we use the Black-Scholes model to take advantage of a European-Style option contract mispricing.")

col1, col2 = st.columns([1,1], gap="small")
        
with col1:
    st.video("https://www.youtube.com/watch?v=0x-Pc-Z3wu4&t=151s&ab_channel=RomanPaolucci")
    st.markdown("10:05 - 13:35 shows how to capitalize using the Black-Scholes")
with col2:
    st.markdown("""
                **1. Understaing "Trading Edge" & Expected Value**
                   - Buying below theoretical value creates a positive expected value situation.
                   - Profitability comes from statistical advantage over many trades, only making one trade may still lose money.
                   
                **2. Long-Run Profitability > Short-Run Noise**
                   - The focus is not on winning every trade, but winning more often.
                   - Avoid blowing the account and losing capital, preserve it to allow the long-run edge to materialize. The edge is worthless if it can't survive to benefit from it.
                """)
                
st.header("📊Black-Scholes Options Contracts:")
st.info("Listed below is a table of options contracts pertaining to a specific stock pulled from Robinhood using the robin_stocks API.", icon="ℹ️")

if "expirations" not in st.session_state:
    st.session_state.expirations = []

if "optionContracts" not in st.session_state:
    st.session_state.optionContracts = []

if "strikes" not in st.session_state:
    st.session_state.strikes = []
    
# === Sidebar Inputs ===
with st.sidebar:
    
    linkedin_url = "https://www.linkedin.com/in/noah-vargas-b04a15290/"

    st.write("`Created by:`")
    st.markdown(
    f"""
    <a href="{linkedin_url}" target="_blank" style="text-decoration: none;">
        <span style="display: flex; align-items: center; gap: 8px;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"
                 width="25" height="25" style="vertical-align: middle; margin-right: 10px;">
            <span style="font-size: 16px; color: white;">Noah Vargas</span>
        </span>
    </a>
    """,
    unsafe_allow_html=True
    )
    
    st.markdown("---")
        
    st.title("Options Pricing Inputs")
    tickers = ["SPY", "QQQ", "TSLA", "AAPL", "NVDA", "SOFI", "GOOGL", "MSFT", "META", "AMD", "PLTR"]
    
    ticker = st.selectbox("Stock Ticker:", options=tickers, placeholder="Please select a stock")
    if ticker:
        try:
            chain = r.options.get_chains(ticker)
            st.session_state.expirations = chain['expiration_dates']
        except Exception as e:
            st.warning(f"Could not load expirations: {e}")
            st.session_state.expirations = []
    selectedExpiration = st.selectbox("Expiration Date:", options=st.session_state.expirations, placeholder="Please select an expiration")
    fetchData = st.button("Fetch Options Data")
    if fetchData and ticker and selectedExpiration:
        try:
            optionContracts = fetchOptionsData(ticker, selectedExpiration)
            strikes = sorted({c.strikePrice for c in optionContracts})
            st.session_state.optionContracts = optionContracts
            st.session_state.strikes = strikes
        except Exception as e:
            st.error(f"Falied to fetch options: {e}")
            st.session_state.optionContracts = []
            st.session_state.strikes = []
    
    st.markdown("---")
    
    st.title("Contract Pricing Inputs")
    selectedStrike = st.selectbox("Strike Price:", options=st.session_state.strikes, disabled=not st.session_state.optionContracts)
    sigmaGuess = st.slider("Enter a Volatility Guess:", min_value=0.01, max_value=1.0)
    
    st.markdown("---")
   
#============================================================================
optionsTable(st.session_state.optionContracts)

with st.expander("ℹ️ What exactly am I looking at? (Options Contracts Table Explanation)"):
    st.markdown("""
                This table displays all available **CALL and PUT** options contracts for the selected stock and expiration date.
                - **Strike Price**: The agreed price to buy (call) or sell (put) the stock.
                - **Time to Maturity**: Days until expiration, expressed as a fraction of a year (used in Black-Scholes calculations).
                - **Call/Put Price**: Market price from Robinhood.
                - **Bid/Ask**: Best current prices to buy/sell each option.
                - **Implied Volatility**: A market-derived estimate of expected future volatility, pulled directly from Robinhood.
                """)

st.markdown("---")

if selectedStrike:
    matches = [c for c in st.session_state.optionContracts if c.strikePrice == selectedStrike]
    if matches:
        st.subheader("📈Selected Option Contract Details:")
        st.info("Listed below is the option contract details for your selected strike. Implied Volatility is calculated using the Newton-Raphson Method to minimize the difference between theoretical and market prices, then calculates the gradient of the Black-Scholes formula. If the Black-Scholes formula outputs a price more expensive than market price, then that contract is undervalued and should be bought.", icon="ℹ️")
        selectedContract = matches[0]
        selectedOption(selectedContract, sigmaGuess)
        with st.expander("ℹ️ What do these numbers mean? (Contract Pricing Breakdown)"):
            st.markdown("""
            You're viewing the **pricing and implied volatility breakdown** for the specific contract you selected:
            
            - **Implied Volatility (Call/Put)**: Computed using **Newton-Raphson root-finding** to back out volatility from the market price using the Black-Scholes formula.
            - **Black-Scholes Price (Call/Put)**: Theoretical price of the option assuming constant volatility and no arbitrage.
            - **Comparison**: You can compare Robinhood's market price with Black-Scholes pricing to see how fair or mispriced the option may be.

            These calculations assume a constant **risk-free rate** (5% default) and no dividend yield.
            """)
        st.markdown("---")
        st.subheader("📑Option Price Heatmaps (Black-Scholes):")
        
        st.info("Listed below are heatmaps generated using the Black-Scholes formula on our real market data.", icon="ℹ️")
        
        spotRange = np.linspace(selectedContract.strikePrice * 0.8, selectedContract.strikePrice * 1.2, 10)
        volRange = np.linspace(0.1, 1.0, 10)
        
        figCall, figPut = plotHeatmaps(selectedContract, spotRange, volRange)
        
        col1, col2 = st.columns([1,1], gap="small")
        
        with col1:
            st.pyplot(figCall)
        with col2:
            st.pyplot(figPut)
            
        with st.expander("ℹ️ What are these heatmaps showing? (Option Price Sensitivity)"):
            st.markdown("""
            These heatmaps show how the **Black-Scholes call and put option prices** respond to changes in:
            
            - **Spot Price** (X-axis): The current price of the stock  
            - **Volatility** (Y-axis): The assumed annualized volatility  

            Each cell displays the theoretical price of the option (call or put) given a specific spot price and volatility.

            ### Why this matters:
            - Helps you visualize how sensitive option prices are to volatility or stock movement
            - Useful for understanding vega exposure
            - Can identify extreme scenarios for stress testing
            """)



        
        




        