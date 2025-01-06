import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os  # To handle folder creation

# Fetch historical data from CoinGecko API
def fetch_historical_data(crypto='ethereum', vs_currency='usd', days=7):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={vs_currency}&days={days}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Check if 'prices' exist and log the data
        if 'prices' not in data:
            raise Exception(f"Invalid data structure: {data}")
        print(f"Data fetched for {crypto}: {data['prices'][:5]}")  # Log first 5 entries
        return data['prices']
    else:
        raise Exception(f"Failed to fetch data from CoinGecko API. Status code: {response.status_code}")

# Prepare and train the model
def train_model(cryptocurrency='ethereum', days=7):
    # Fetch historical data
    prices = fetch_historical_data(cryptocurrency, 'usd', days)

    # Prepare the data for training
    dates = [x[0] for x in prices]  # Get timestamps
    prices_only = [x[1] for x in prices]  # Get prices

    # Convert timestamps to date objects and then to the number of days since the first date
    df = pd.DataFrame({
        'dates': pd.to_datetime(dates, unit='ms'),
        'prices': prices_only
    })
    df['days_since'] = (df['dates'] - df['dates'].min()).dt.days

    # Check for missing data
    print("Training data preview:")
    print(df.head())
    print("Missing values in data:", df.isnull().sum())

    # Drop rows with missing values if any
    df = df.dropna()

    # Features and target
    X = df[['days_since']]  # Features (number of days since start)
    y = df['prices']  # Target (prices)

    # Train a Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Create the 'models' folder if it does not exist
    model_folder = 'models'
    os.makedirs(model_folder, exist_ok=True)

    # Save the trained model into the 'models' folder
    model_path = os.path.join(model_folder, f'{cryptocurrency}_model.pkl')
    print(f"Saving model to: {model_path}")
    joblib.dump(model, model_path)

    print(f"Model trained and saved successfully at {model_path}!")

# Example: Train model for Ethereum (you can replace with any crypto)
train_model('ethereum', 7)
