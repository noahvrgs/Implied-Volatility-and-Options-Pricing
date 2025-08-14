Black-Scholes Option Pricing App

Welcome!
This project demonstrates Black-Scholes option pricing using real Robinhood options data, fetched via the robin_stocks API, and displayed in an interactive Streamlit dashboard.

🚀 Getting Started
1️⃣ Fork the Repository

Click the Fork button at the top-right of this page to copy the repo into your own GitHub account.

2️⃣ Set Up Environment Variables

Create a .env file in the root project folder and add your Robinhood login credentials:

ROBINHOOD_USERNAME=your_robinhood_username
ROBINHOOD_PASSWORD=your_robinhood_password


Note: These credentials are required to use the robin_stocks API. They are not stored anywhere — authentication happens at runtime only.

3️⃣ Install Dependencies

From your terminal:

pip install robin_stocks

4️⃣ Run the App

In the project directory, start the Streamlit app:

streamlit run app.py

5️⃣ Enjoy!

Explore live Black-Scholes pricing, volatility calculations, and interactive visualizations.

⚠️ Important Notice

Credentials Safety: Your Robinhood username and password are only used locally and never saved or transmitted anywhere outside the API request.

Educational Use: This project is for educational purposes only and is not financial advice.
