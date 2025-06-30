import numpy as np
from scipy.stats import norm

class BlackScholes:
    def __init__(
        self,
        expireDate: float,
        strikePrice: float,
        sharePrice: float,
        volatility: float,
        interestRate: float
    ):
        self.expireDate = expireDate
        self.strikePrice = strikePrice
        self.sharePrice = sharePrice
        self.volatility = volatility
        self.interestRate = interestRate
    

    def blackScholesCalculation(self):
        S = self.sharePrice
        K = self.strikePrice
        T = self.expireDate
        r = self.interestRate
        sigma = self.volatility
        
        d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        callPrice = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        putPrice = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        self.callPrice = callPrice
        self.putPrice = putPrice
        
        return callPrice, putPrice
        

