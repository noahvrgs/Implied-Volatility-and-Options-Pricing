# === Import Libraries ===
import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
from datetime import datetime
import yfinance as yf
import robin_stocks.robinhood as r
from robin_stocks.robinhood import options
from dataclasses import dataclass
import jax.numpy as jnp
from jax.scipy.stats import norm
from jax import grad

# === Class Data Structures ===
class OptionContract:
    def __init__(self, 
                 ticker, 
                 strikePrice, 
                 expiration, 
                 timeToMaturity, 
                 bidPrice, 
                 askPrice, 
                 callPrice, 
                 putPrice, 
                 volatilityRobinhood
                 ):
        self.ticker = ticker
        self.strikePrice = float(strikePrice) if strikePrice is not None else None
        self.expiration = expiration
        self.timeToMaturity = float(timeToMaturity) if timeToMaturity is not None else None
        self.bidPrice = float(bidPrice) if bidPrice is not None else None
        self.askPrice = float(askPrice) if askPrice is not None else None
        self.callPrice = float(callPrice) if callPrice is not None else None
        self.putPrice = float(putPrice) if putPrice is not None else None
        self.volatilityRobinhood = float(volatilityRobinhood) if volatilityRobinhood is not None else None
        
        self.riskFreeRate = 0.05
        self.volatilityCallValue = None
        self.volatilityPutValue = None
        self.blackScholesCallValue = None
        self.blackScholesPutValue = None
        
        
    def blackScholesCalculation(self, S: float, sigma: float, optionType: str) -> float:
        K = self.strikePrice
        T = self.timeToMaturity
        rfr = self.riskFreeRate
            
        d1 = (jnp.log(S/K) + (rfr + 0.5 * sigma**2) * T) / (sigma * jnp.sqrt(T))
        d2 = d1 - sigma * jnp.sqrt(T)
        if optionType == 'call':
            return S * norm.cdf(d1) - K * jnp.exp(-rfr * T) * norm.cdf(d2)
        elif optionType == 'put':
            return K * jnp.exp(-rfr * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    def impliedVolatilityCalculation(self, S:float, sigmaGuess: float, optionType: str) -> float:
        maxIterations = 20
        epsilon = 0.001
    
        K = self.strikePrice
        T = self.timeToMaturity
        riskFreeRate = self.riskFreeRate
            
        if optionType == "call":
            optionPrice = self.callPrice
        elif optionType == "put":
            optionPrice = self.putPrice
                
        converged = False
        lossGradient = grad(self.lossCalculation, argnums=1) #Might need to change this
            
        sigma = sigmaGuess
        for i in range(maxIterations):
            lossValue = self.lossCalculation(S, sigma, optionType)
            if abs(lossValue) < epsilon:
                converged = True
                break
            else:
                lossGradientValue = lossGradient(S, sigma, optionType)
                if abs(lossGradientValue) < 1e-8:
                    print("Gradient near zero — stopping iteration")
                    break
                sigma = sigma - lossValue / lossGradientValue
            
        if not converged:
            print("Did not converge")
        return sigma     
                                            
    def lossCalculation(self, S:float, sigma: float, optionType: str) -> float:
            
        if optionType == "call":
            optionPrice = self.callPrice
        elif optionType == "put":
            optionPrice = self.putPrice
                
        theoreticalPrice = self.blackScholesCalculation(S, sigma, optionType)
        marketPrice = optionPrice
            
        return theoreticalPrice - marketPrice
    
    def getSharePrice(self, ticker: str) -> float:
        price = r.stocks.get_latest_price(ticker, includeExtendedHours=False)
        return float(price[0]) if price and price[0] else None
              
# === Utility/Calculation Functions ===
def robinhoodLogin():
    if 'rh_logged_in' not in st.session_state:
        try:
            r.login(os.getenv("ROBINHOOD_USERNAME"), os.getenv("ROBINHOOD_PASSWORD"))
            st.session_state['rh_logged_in'] = True
            st.success("Robinhood Login Successful")
        except Exception as e:
            st.session_state['rh_logged_in'] = False
            st.error(f"Robinhood Login Failed: {e}")

@st.cache_data(ttl=300) #Cache Options Data for 5 Minutes
def fetchOptionsData(ticker: str, expirationDate: str):
    contracts = []
    try:
        calls = r.options.find_options_by_expiration(ticker, expirationDate, optionType='call')
        puts = r.options.find_options_by_expiration(ticker, expirationDate, optionType='put')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    
    call_map = {float(opt['strike_price']): opt for opt in calls}
    put_map = {float(opt['strike_price']): opt for opt in puts}

    all_strikes = sorted(set(call_map.keys()) | set(put_map.keys()))
    
    for strike in all_strikes:
        call = call_map.get(strike)
        put = put_map.get(strike)

        callPrice = float(call['mark_price']) if call and call['mark_price'] else None
        putPrice = float(put['mark_price']) if put and put['mark_price'] else None
        
        bidPrice = float(call['bid_price']) if call and call['bid_price'] else None
        askPrice = float(call['ask_price']) if call and call['ask_price'] else None
        volatilityRobinhood = float(call['implied_volatility']) if call and call['implied_volatility'] else None

        contract = OptionContract(
            ticker=ticker,
            strikePrice=strike,
            expiration=expirationDate,
            timeToMaturity=timeToMaturityCalc(expirationDate),
            callPrice=callPrice,
            putPrice=putPrice,
            bidPrice=bidPrice,
            askPrice=askPrice,
            volatilityRobinhood=volatilityRobinhood
        )

        contracts.append(contract)

    return contracts

def timeToMaturityCalc(expirationInput: str) -> float:
    expirationDate = datetime.strptime(expirationInput, "%Y-%m-%d").date()
    today = datetime.today().date()
    daysToExpiration = (expirationDate - today).days
    T = daysToExpiration / 365 # 252: Trading Days or 365: Standard
    return max(T, 0)

def isContractExpired():
    pass











