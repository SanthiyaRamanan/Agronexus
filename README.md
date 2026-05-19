# 🌾 AgroNexus — Full-Stack Agriculture Platform

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Vanilla JS, Chart.js
- **Database**: MySQL (via MySQL Workbench)
- **AI/ML**: Python (scikit-learn, numpy, pandas)
- **Auth**: bcrypt password hashing

---

## 📁 Project Structure

```
agri_project/
├── app.py                    ← Main Flask application
├── requirements.txt          ← Python dependencies
├── database/
│   └── schema.sql            ← Run this in MySQL Workbench first!
├── ml_models/
│   ├── price_predictor.py    ← AI price prediction model
│   ├── crop_advisor.py       ← Crop recommendation engine
│   ├── quality_grader.py     ← AI quality grading
│   └── scheme_matcher.py     ← Government scheme matcher
├── templates/
│   ├── base.html             ← Base layout with sidebar + chatbot
│   ├── index.html            ← Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html        ← Main dashboard with charts
│   ├── marketplace.html      ← Crop marketplace
│   ├── listing_detail.html   ← Crop detail + auction bids
│   ├── add_listing.html      ← Sell crops form
│   ├── equipment.html        ← Equipment rental
│   ├── add_equipment.html    ← List equipment form
│   ├── ai_tools.html         ← All 4 AI tools
│   ├── my_listings.html      ← User profile/history
│   └── govt_dashboard.html   ← Government analytics
└── static/
    ├── css/
    ├── js/
    └── images/uploads/
```

---

## 🚀 Setup Instructions

### Step 1: MySQL Workbench Setup
1. Open MySQL Workbench
2. Connect to your local MySQL server
3. Open `database/schema.sql`
4. Click ⚡ to execute the full script
5. This creates the `agri_platform` database with all tables + seed data

### Step 2: Configure Database in app.py
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'YOUR_PASSWORD'   # ← Change this
app.config['MYSQL_DB'] = 'agri_platform'
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the App
```bash
python app.py
```

### Step 5: Open in Browser
```
http://localhost:5000
```

---

## 👥 Test Accounts (after running schema.sql)

| Role | Email | Password |
|------|-------|----------|
| Govt Admin | govt@agri.com | (set manually) |

Register new accounts via the web interface for Farmer/Buyer/Rental roles.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🛒 Marketplace | Buy/sell crops directly, filter by crop & location |
| 🔨 Live Auction | Place bids on crop listings in real-time |
| 💳 Buy Now | Instant purchase with automatic inventory update |
| 🚜 Equipment Rental | Rent equipment by the hour |
| 🔧 List Equipment | Earn by listing your own machinery |
| 📈 Price Prediction | ML-based 7-day price forecast per crop |
| 🌾 Crop Advisor | Location + soil + season based recommendations |
| ⭐ Quality Grader | A/B/C quality assessment with price impact |
| 🏛️ Scheme Matcher | AI matches you to eligible govt schemes |
| 💬 AgroBot | In-app chatbot for quick queries |
| 📊 Govt Dashboard | Analytics for government users |
| 🔐 Auth System | Secure login/register with bcrypt |

---

## 🧠 Upgrading AI Models (Production)

Replace the mock ML functions in `ml_models/` with:
- **Price Predictor**: Train `LinearRegression` or `ARIMA` on `price_history` table
- **Crop Advisor**: Train `DecisionTreeClassifier` on agro-climatic datasets
- **Quality Grader**: Use `CNN` (MobileNet) for image-based grading
- **Scheme Matcher**: Rule-based NLP with `spaCy` for natural language queries

---

## 📞 Built by
**Santhiya R** — AgroNexus Project 2024
