import robin_stocks.robinhood as r
from robin_stocks.robinhood import options
import pandas as pd
import time
import os
import streamlit as st

#-------------------------------------------------------------------------------------------------------------
def robinhoodLogin():
    
    '''
    - Robinhood login using .env credentials
    - Checks if recently logged in to avoid verfication again
    - Return Type: void
    '''
    
    if 'rh_logged_in' not in st.session_state:
        try: 
            r.login(os.getenv("ROBINHOOD_USERNAME"), os.getenv("ROBINHOOD_PASSWORD"))
            st.session_state['rh_logged_in'] = True
            st.success("Robinhood Login Success")
            
        except Exception as e:
            st.session_state['rh_logged_in'] = False
            st.error(f"Robinhood Login Failed: {e}")
    
#-------------------------------------------------------------------------------------------------------------

def fetchOptionsData(ticker, expireDate, csv = "options_data.csv"):
    
    '''
        - Uses the robin_stocks API to fetch a certain stock's option contracts
        - Gets data and writes to a CSV file
        - Return type: void
    '''
    
    optionsChain = r.options.find_options_by_expiration(ticker, expireDate, optionType=None, info=None)
    allOptions = []
    
    for opt in optionsChain:
        try:
            option_type = opt["type"]
            if option_type not in ["call", "put"]:
                print("Skipping option with unknown type:", opt)
                continue
            
            allOptions.append({
                "strike": float(opt["strike_price"]),
                "expiration": opt["expiration_date"],
                "type": option_type,
                "implied_volatility": float(opt["implied_volatility"]),
                "ask_price": float(opt["ask_price"]),
                "bid_price": float(opt["bid_price"]),
                "mid_price": (float(opt["ask_price"]) + float(opt["bid_price"])) / 2,
            })
            
            print("Available Expirations Dates: ", opt)
            
        except:
            continue
    
    if not allOptions:
        print("No valid options data fetched.")
        return
    
    df = pd.DataFrame(allOptions)
    
    df_call = df[df["type"] == "call"].copy()
    df_call.rename(columns={"mid_price": "call_price"}, inplace=True)
    
    df_put = df[df["type"] == "put"].copy()
    df_put.rename(columns={"mid_price": "put_price"}, inplace=True)

    merged = pd.merge(df_call, df_put, on=["strike", "expiration"], how="outer", suffixes=("_call", "_put"))

    final_df = merged[[
        "strike", "expiration", "call_price", "put_price",
        "implied_volatility_call", "implied_volatility_put"
    ]].copy()

    final_df["implied_volatility"] = final_df[["implied_volatility_call", "implied_volatility_put"]].mean(axis=1)
    final_df.drop(columns=["implied_volatility_call", "implied_volatility_put"], inplace=True)

    final_df.to_csv(csv, index=False)
    print(f"Saved {len(final_df)} options to {csv}")
    
