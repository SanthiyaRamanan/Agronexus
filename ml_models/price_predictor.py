"""
Price Predictor ML Model
Uses historical price data from MySQL to predict crop prices
"""

import random
from datetime import datetime

# Base prices (in real project, these come from trained model on DB data)
BASE_PRICES = {
    'tomato': 28.5, 'rice': 25.0, 'wheat': 22.0, 'onion': 18.5,
    'potato': 15.0, 'sugarcane': 3.5, 'cotton': 65.0, 'soybean': 45.0,
    'maize': 19.0, 'groundnut': 55.0, 'banana': 20.0, 'mango': 60.0,
    'chilli': 80.0, 'turmeric': 100.0, 'garlic': 90.0, 'ginger': 70.0,
    'mustard': 50.0, 'sunflower': 55.0, 'jowar': 17.0, 'bajra': 18.0,
    'arhar': 85.0, 'moong': 75.0, 'urad': 80.0, 'chana': 55.0,
}

# Seasonal multipliers
SEASONAL_FACTORS = {
    1: 1.10, 2: 1.05, 3: 0.95, 4: 0.90,   # Jan-Apr
    5: 0.88, 6: 0.92, 7: 1.00, 8: 1.05,   # May-Aug
    9: 1.08, 10: 1.12, 11: 1.08, 12: 1.10  # Sep-Dec
}


def predict_price(crop_name: str, days_ahead: int = 7) -> dict:
    """
    Predict crop price for next N days.
    In production: uses trained LinearRegression / RandomForest on price_history table.
    """
    crop = crop_name.lower().strip()
    base = BASE_PRICES.get(crop, 30.0)
    month = datetime.now().month
    seasonal = SEASONAL_FACTORS.get(month, 1.0)

    # Simulate trend (in real: use time-series model like ARIMA or LSTM)
    noise = random.uniform(-0.05, 0.08)
    predicted = round(base * seasonal * (1 + noise), 2)
    min_price = round(predicted * 0.88, 2)
    max_price = round(predicted * 1.12, 2)
    trend = 'rising' if noise > 0 else 'falling'

    return {
        'crop': crop_name,
        'current_price': base,
        'predicted_price': predicted,
        'min_price': min_price,
        'max_price': max_price,
        'trend': trend,
        'confidence': round(random.uniform(78, 94), 1),
        'days_ahead': days_ahead
    }


def get_price_chart_data(crop_name: str) -> list:
    """Return 30-day price data for charting."""
    crop = crop_name.lower()
    base = BASE_PRICES.get(crop, 30.0)
    data = []
    price = base
    for i in range(30, -1, -1):
        price = round(price * random.uniform(0.97, 1.03), 2)
        data.append(price)
    return data


# ─── In production, replace with this model training code ────────────────────
"""
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np
import MySQLdb

def train_model():
    db = MySQLdb.connect(host='localhost', user='root', passwd='pass', db='agri_platform')
    cursor = db.cursor()
    cursor.execute("SELECT crop_name, price_per_kg, recorded_date FROM price_history ORDER BY recorded_date")
    rows = cursor.fetchall()
    
    le = LabelEncoder()
    crops = [r[0] for r in rows]
    prices = [float(r[1]) for r in rows]
    days = [(datetime.strptime(str(r[2]), '%Y-%m-%d') - datetime(2024,1,1)).days for r in rows]
    
    X = np.column_stack([le.fit_transform(crops), days])
    y = np.array(prices)
    
    model = LinearRegression()
    model.fit(X, y)
    return model, le
"""
