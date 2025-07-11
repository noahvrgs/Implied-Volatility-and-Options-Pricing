import numpy as np
import matplotlib as mpl
from scipy.stats import norm
from jax import grad


def blackScholesCalculation(S, K, T, r, sigma, optionType): 
    '''
        - S: Current stock price
        - K: Strike price
        - T: Time to expiration (in years)
        - r: Risk-free interest rate (typically 5%)
        - sigma: Volatility (not given)
        - optionType: either call or put
    '''
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if optionType == 'call':
        callPrice = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return callPrice
    elif optionType == 'put':
        putPrice = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return callPrice, putPrice
    else:
        print("Please enter a valid option type.")




def loss(S, K, T, r, sigmaGuess, price, optionType):
    '''
    - Loss is the difference between the theoretical price and the market price
    - We want to minimize the amount of loss (close to 0)
    '''
    theoreticalPrice = blackScholesCalculation(S, K, T, r, sigmaGuess, optionType)
    marketPrice = price
    return theoreticalPrice - marketPrice




def impliedVolatilityCalculation(S, K, T, r, sigmaGuess, price, optionType, maxIterations = 20, epsilon = 0.001, verbose = True):
    '''
    - We will calculate an options implied volatility by using the Newton-Raphson method
    '''
    converged = False
    lossGradient = grad(loss, argnums = 4)
    
    # Step 1: Make a guess for the volatility
    sigma = sigmaGuess
    for i in range(maxIterations):
        
        # Step 2: Calculate the loss function
        lossValue = loss(S, K, T, r, sigma, price, optionType)
        
        if verbose:
            print("\nIteration: ", i)
            print("Error in Theoretical vs. Market Price:")
            print(lossValue)
            
        # Step 3: Check if loss is less than epsilon (tolerance)
        if abs(lossValue) < epsilon:
            converged = True
            break
        
        else:
            # Step 4: Calculate the gradient of the loss function
            lossGradientValue = lossGradient(S, K, T, r, sigma, price, optionType)
            
            if verbose:
                print("Gradient: ", lossGradientValue)
            
            # Step 5: Update the volatility using the Newton-Raphson formula
            sigma = sigma - lossValue / lossGradientValue
            
            if verbose:
                print("New Sigma (Volatility): ", sigma)
    
    if not converged:
        print("Did not converge")
    return sigma


        
