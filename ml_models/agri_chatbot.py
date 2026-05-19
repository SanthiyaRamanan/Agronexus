"""
AgroNexus NLP Chatbot — ML-powered Agriculture Assistant
=========================================================
Save this file as:  ml_models/agri_chatbot.py

Algorithm  : TF-IDF Vectorizer + Logistic Regression (multinomial)
Intents    : 14 agriculture-specific intents
Training   : 250+ hand-crafted utterances
Features   : Entity extraction, context memory, personalized replies
Install    : pip install scikit-learn numpy
"""

import re
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# ══════════════════════════════════════════════════════════════════
# 1.  TRAINING DATA
#     Format:  intent_name -> [list of example sentences]
# ══════════════════════════════════════════════════════════════════
INTENT_DATA = {

    # ── prices ────────────────────────────────────────────────────
    "crop_price": [
        "what is the price of tomato",
        "tomato rate today",
        "how much is rice selling for",
        "current price of wheat",
        "onion price in market",
        "potato rate per kg",
        "what is the market price of cotton",
        "tell me price of chilli",
        "mango price today",
        "soybean current rate",
        "groundnut price",
        "sugarcane rate",
        "maize price today",
        "price of turmeric",
        "garlic rate per kg",
        "mustard seed price",
        "bajra market rate",
        "jowar price per quintal",
        "urad dal price",
        "moong dal current price",
        "arhar dal rate",
        "crop price today",
        "today vegetable rate",
        "mandi price",
        "what should I sell my crop for",
        "how much will I get for my tomatoes",
        "wheat mandi rate",
        "paddy price today",
        "cotton price per quintal",
        "soybean mandi rate today",
    ],

    # ── price forecast ────────────────────────────────────────────
    "price_prediction": [
        "will tomato price increase",
        "predict rice price next week",
        "what will wheat cost tomorrow",
        "future price of onion",
        "should I sell now or wait",
        "price forecast for cotton",
        "expected price of soybean",
        "will crop prices go up",
        "price trend for maize",
        "when to sell my crop for best price",
        "price prediction for chilli",
        "market forecast for groundnut",
        "is this a good time to sell tomato",
        "hold or sell my rice",
        "price outlook for next month",
        "onion price next week prediction",
        "will wheat price rise",
        "tomato price trend",
        "best time to sell potato",
        "chilli price forecast",
    ],

    # ── crop recommendation ───────────────────────────────────────
    "crop_recommendation": [
        "which crop should I grow",
        "what crop is best for my land",
        "suggest crops for this season",
        "best crop for clay soil",
        "what to grow in summer",
        "rabi crop recommendation",
        "kharif crop suggestion",
        "which crop grows well in Tamil Nadu",
        "best crop for Punjab",
        "what to plant in black soil",
        "crop for sandy soil",
        "which crop needs less water",
        "high yield crop recommendation",
        "profitable crop to grow",
        "seasonal crop advice",
        "what crop for loamy soil",
        "crop suitable for dry regions",
        "crop for rainy season",
        "organic crop recommendation",
        "best vegetable to grow now",
        "which crop gives more profit",
        "crop rotation advice",
        "intercropping suggestion",
        "best crop for Karnataka",
        "crop for Maharashtra black soil",
    ],

    # ── fertilizer ────────────────────────────────────────────────
    "fertilizer_advice": [
        "how much fertilizer to use",
        "which fertilizer for wheat",
        "NPK ratio for tomato",
        "fertilizer dose for rice",
        "urea application for maize",
        "organic fertilizer for vegetables",
        "DAP fertilizer advice",
        "potash for cotton",
        "fertilizer schedule for sugarcane",
        "micronutrient deficiency in crop",
        "how to improve soil fertility",
        "compost or chemical fertilizer",
        "fertilizer for sandy soil",
        "nitrogen deficiency symptoms",
        "phosphorus for root development",
        "boron deficiency in crops",
        "zinc deficiency treatment",
        "how often to apply fertilizer",
        "fertilizer for leafy vegetables",
        "best fertilizer for onion",
        "when to apply urea",
        "DAP vs NPK which is better",
        "vermicompost benefits",
        "fertilizer for paddy crop",
        "how to correct yellow leaves",
    ],

    # ── pest and disease ──────────────────────────────────────────
    "pest_disease": [
        "my crop has yellow leaves",
        "pest attack on tomato",
        "how to treat fungal disease in wheat",
        "insects on my rice crop",
        "caterpillar infestation cotton",
        "blast disease in paddy",
        "how to control aphids",
        "white fly on chilli",
        "stem borer in maize",
        "blight in potato",
        "powdery mildew on grapes",
        "leaf curl virus tomato",
        "how to spray pesticide",
        "organic pest control",
        "disease resistant crop varieties",
        "neem spray for pest",
        "my plants are dying",
        "brown spots on leaves",
        "crop wilting suddenly",
        "early blight late blight treatment",
        "thrips on onion",
        "mealy bug infestation",
        "fruit borer in brinjal",
        "downy mildew control",
        "rust disease in wheat",
    ],

    # ── irrigation ────────────────────────────────────────────────
    "irrigation": [
        "how much water for tomato",
        "irrigation schedule for wheat",
        "drip irrigation for vegetables",
        "sprinkler vs drip irrigation",
        "water requirement for rice",
        "irrigation frequency for cotton",
        "how often to water sugarcane",
        "water saving techniques in farming",
        "when to irrigate crops",
        "flood irrigation vs drip",
        "irrigation for dry season",
        "soil moisture management",
        "rainwater harvesting for farming",
        "water logging problem solution",
        "irrigation for sandy soil",
        "how to set up drip system",
        "micro irrigation benefits",
        "furrow irrigation method",
        "overhead irrigation for vegetables",
        "irrigation timing morning or evening",
    ],

    # ── government schemes ────────────────────────────────────────
    "govt_schemes": [
        "what government schemes are available for farmers",
        "PM KISAN scheme details",
        "how to apply for PMFBY",
        "kisan credit card apply",
        "crop insurance scheme",
        "government subsidy for tractor",
        "free seeds from government",
        "soil health card scheme",
        "eNAM registration",
        "RKVY scheme benefits",
        "SMAM equipment subsidy",
        "how to get farm loan",
        "government help for small farmers",
        "agriculture scheme for SC ST farmers",
        "organic farming scheme",
        "pradhan mantri fasal bima yojana",
        "PM kisan samman nidhi money",
        "am I eligible for government scheme",
        "subsidy for drip irrigation",
        "how much money under PM KISAN",
        "NABARD scheme for farmers",
        "government grant for agriculture",
        "pension scheme for farmers",
        "input subsidy scheme",
        "agricultural insurance claim",
    ],

    # ── equipment rental ──────────────────────────────────────────
    "equipment_rental": [
        "rent a tractor",
        "how to rent harvester",
        "tractor rental near me",
        "equipment hire for farming",
        "cost of renting combine harvester",
        "CRM machine rental",
        "crop residue machine hire",
        "sprayer rental",
        "ploughing machine rent",
        "seeder machine hire",
        "how much to rent a tractor per hour",
        "where can I find rental equipment",
        "farm machinery on rent",
        "tractor booking online",
        "equipment for small farmers",
        "rotavator hire",
        "power tiller rental",
        "thresher machine rent",
        "laser land leveller hire",
        "paddy transplanter rental",
    ],

    # ── selling crops ─────────────────────────────────────────────
    "selling_crops": [
        "how to sell my crops",
        "where to sell tomatoes",
        "best market for vegetables",
        "sell crops online",
        "direct selling to buyers",
        "get better price for my crop",
        "mandi vs online selling",
        "how to list my crop for sale",
        "find buyers for rice",
        "export my crops",
        "wholesale market for farmers",
        "FPO selling benefits",
        "group selling advantage",
        "how to avoid middlemen",
        "best platform to sell crops",
        "sell wheat directly to miller",
        "online mandi for farmers",
        "commission agent problem",
        "how to get fair price for crops",
        "farmer market linkage",
    ],

    # ── weather ───────────────────────────────────────────────────
    "weather": [
        "what is the weather today",
        "will it rain this week",
        "weather forecast for farming",
        "temperature today",
        "monsoon forecast",
        "is it good weather for sowing",
        "frost warning for crops",
        "heatwave effect on crops",
        "weather advisory for farmers",
        "cyclone warning",
        "humidity today",
        "when will monsoon arrive",
        "dry spell forecast",
        "rainfall prediction",
        "pre monsoon showers",
        "cold wave advisory",
        "weather for harvesting",
        "fog effect on crops",
        "wind speed today",
        "climate change effect on farming",
    ],

    # ── soil health ───────────────────────────────────────────────
    "soil_health": [
        "how to test soil",
        "my soil is not fertile",
        "how to improve soil quality",
        "soil pH for tomato",
        "acidic soil treatment",
        "how to reduce soil salinity",
        "organic matter in soil",
        "black cotton soil properties",
        "red soil farming tips",
        "sandy soil improvement",
        "clay soil drainage problem",
        "soil health card how to get",
        "compost making at home",
        "vermicompost preparation",
        "green manure crops list",
        "soil erosion prevention",
        "saline soil reclamation",
        "gypsum for alkaline soil",
        "lime for acidic soil",
        "soil microbiome health",
    ],

    # ── loans and finance ─────────────────────────────────────────
    "loan_finance": [
        "how to get farm loan",
        "kisan credit card interest rate",
        "agriculture loan without collateral",
        "NABARD loan for farmers",
        "crop loan apply",
        "interest subvention scheme",
        "loan for tractor purchase",
        "micro finance for farmers",
        "loan waiver scheme",
        "bank loan for agriculture",
        "SHG loan for farming",
        "short term crop loan",
        "agricultural gold loan",
        "how much loan can farmer get",
        "cooperative bank loan",
        "loan for cold storage",
        "agri infrastructure fund",
        "loan for drip irrigation",
        "farm loan repayment",
        "crop loan interest rate 2024",
    ],

    # ── post harvest ──────────────────────────────────────────────
    "post_harvest": [
        "how to store onion",
        "storage tips for potatoes",
        "cold storage for vegetables",
        "post harvest loss reduction",
        "grading and sorting crops",
        "packaging for market",
        "how long can tomatoes be stored",
        "drying chilli properly",
        "rice storage tips",
        "warehouse facility for farmers",
        "food processing for farmers",
        "value addition to crops",
        "how to avoid crop spoilage",
        "mango ripening techniques",
        "dal milling process",
        "onion curing process",
        "hermetic bag for grain storage",
        "cold chain management",
        "post harvest disease control",
        "packaging material for vegetables",
    ],

    # ── greeting ──────────────────────────────────────────────────
    "greeting": [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good evening",
        "good afternoon",
        "namaste",
        "vanakkam",
        "how are you",
        "who are you",
        "what can you do",
        "help me",
        "I need help",
        "start",
        "hi there",
        "hey bot",
        "hello agrobot",
        "what do you know",
        "what are your features",
        "tell me about yourself",
    ],

    # ── thanks ────────────────────────────────────────────────────
    "thanks": [
        "thank you",
        "thanks",
        "thank you so much",
        "that was helpful",
        "great thanks",
        "ok thanks",
        "got it thanks",
        "very helpful",
        "appreciate it",
        "thanks a lot",
        "bahut shukriya",
        "nandri",
        "dhanyavaad",
        "super helpful",
        "perfect thanks",
    ],
}


# ══════════════════════════════════════════════════════════════════
# 2.  RESPONSE TEMPLATES — one intent → multiple reply variants
#     A random one is chosen on each call for natural variety
# ══════════════════════════════════════════════════════════════════
RESPONSES = {

    "crop_price": [
        (
            "📊 Current market prices:\n"
            "🍅 Tomato   : ₹25–32 /kg\n"
            "🌾 Rice     : ₹22–28 /kg\n"
            "🌾 Wheat    : ₹20–25 /kg\n"
            "🧅 Onion    : ₹15–22 /kg\n"
            "🥔 Potato   : ₹12–18 /kg\n"
            "🌸 Cotton   : ₹60–70 /kg\n"
            "🌽 Maize    : ₹18–22 /kg\n"
            "🌶️ Chilli   : ₹75–92 /kg\n\n"
            "💡 For live AI forecast → use 📈 Price Prediction in AI Tools!"
        ),
        (
            "💰 Today's mandi rates (approx):\n"
            "• Tomato    ₹25–30 /kg\n"
            "• Wheat     ₹20–24 /kg\n"
            "• Onion     ₹14–20 /kg\n"
            "• Turmeric  ₹95–115 /kg\n"
            "• Groundnut ₹50–62 /kg\n"
            "• Soybean   ₹42–50 /kg\n\n"
            "Prices vary by location & grade. "
            "Use the AI Price Predictor for your specific crop & region!"
        ),
    ],

    "price_prediction": [
        (
            "🤖 Our ML Price Predictor uses:\n"
            "• Historical mandi price data\n"
            "• Seasonal demand patterns\n"
            "• Weather impact modelling\n"
            "• Supply-chain signals\n\n"
            "Go to 📈 AI Tools → Price Prediction, select your crop "
            "and get a 7-day forecast with confidence score!"
        ),
        (
            "📈 Current price trends:\n"
            "• Tomato   → Rising ↑  (consider holding 2–3 days)\n"
            "• Onion    → Falling ↓ (sell soon)\n"
            "• Rice     → Stable  →\n"
            "• Wheat    → Slight rise ↑\n"
            "• Cotton   → Rising ↑\n\n"
            "For accurate crop-specific prediction → AI Tools → Price Prediction!"
        ),
    ],

    "crop_recommendation": [
        (
            "🌾 Crop recommendations by season & soil:\n\n"
            "🌱 Kharif (Jun–Nov):\n"
            "  Clay  → Paddy, Sugarcane, Cotton\n"
            "  Loamy → Maize, Soybean, Sunflower\n"
            "  Sandy → Groundnut, Pearl Millet\n\n"
            "❄️ Rabi (Nov–Apr):\n"
            "  Loamy → Wheat, Mustard, Potato\n"
            "  Black → Chickpea, Sorghum\n\n"
            "For personalised advice → 🌾 Crop Advisor in AI Tools!"
        ),
        (
            "💡 Top profitable crops right now:\n"
            "1. 🍅 Tomato    — High demand, 60–90 day cycle\n"
            "2. 🌶️ Chilli   — Strong export demand\n"
            "3. 🧅 Onion     — Stable prices year-round\n"
            "4. 🥔 Potato    — Quick returns\n"
            "5. 🌾 Wheat     — Guaranteed MSP support\n"
            "6. 🌸 Cotton    — Good for black soil regions\n\n"
            "Tell me your state and soil type for better suggestions!"
        ),
    ],

    "fertilizer_advice": [
        (
            "🧪 Standard NPK recommendations:\n"
            "• Rice      : 120 : 60 : 60  kg/ha\n"
            "• Wheat     : 120 : 60 : 40  kg/ha\n"
            "• Tomato    : 150 : 75 : 75  kg/ha\n"
            "• Cotton    : 180 : 80 : 80  kg/ha\n"
            "• Maize     : 180 : 60 : 40  kg/ha\n"
            "• Sugarcane : 250 :100 :100  kg/ha\n\n"
            "⚠️ Get a FREE Soil Health Card first for precise doses!"
        ),
        (
            "🌱 Fertilizer best practices:\n"
            "• Split urea — 50% at sowing, 50% top-dress\n"
            "• DAP is best applied at sowing\n"
            "• Zinc sulphate (25 kg/ha) fixes yellowing\n"
            "• Compost improves soil long-term\n"
            "• Never over-apply — causes salt stress!\n\n"
            "Visit nearest KVK for free soil testing & recommendations."
        ),
    ],

    "pest_disease": [
        (
            "🐛 Common pest solutions:\n"
            "• Aphids / Whitefly → Neem oil 5 ml/L water\n"
            "• Stem borer        → Carbofuran 3G in soil\n"
            "• Caterpillars      → BT (Bacillus thuringiensis) spray\n"
            "• Leaf curl virus   → Remove infected plants + control whitefly\n"
            "• Fungal disease    → Mancozeb or Copper oxychloride\n\n"
            "💡 Upload crop photo in Quality Grader for AI diagnosis!"
        ),
        (
            "🌿 Disease identification guide:\n"
            "• Yellow leaves   → N deficiency or root rot\n"
            "• Brown spots     → Early blight → use Mancozeb\n"
            "• White powder    → Powdery mildew → sulphur spray\n"
            "• Sudden wilting  → Fusarium wilt or water stress\n"
            "• Paddy blast     → Tricyclazole spray immediately\n"
            "• Rust in wheat   → Propiconazole fungicide\n\n"
            "Use IPM (Integrated Pest Management) to reduce chemicals!"
        ),
    ],

    "irrigation": [
        (
            "💧 Crop water requirements:\n"
            "• Rice       : 1200–2000 mm (high)\n"
            "• Wheat      :  400–500 mm\n"
            "• Tomato     :  400–600 mm\n"
            "• Cotton     :  700–1300 mm\n"
            "• Sugarcane  : 1500–2500 mm\n"
            "• Maize      :  500–800 mm\n\n"
            "💡 Drip irrigation saves 40–50% water vs flood. "
            "PMKSY scheme gives 55% subsidy on drip installation!"
        ),
        (
            "💧 Smart irrigation tips:\n"
            "• Irrigate early morning — reduces evaporation\n"
            "• Check soil moisture before irrigating\n"
            "• Drip: 2–4 hrs/day depending on crop stage\n"
            "• Rabi crops: irrigate every 10–15 days\n"
            "• Avoid irrigation just before harvest\n"
            "• Mulching reduces water loss by 30%\n\n"
            "Apply for PMKSY drip subsidy at your district agriculture office!"
        ),
    ],

    "govt_schemes": [
        (
            "🏛️ Key schemes for farmers:\n\n"
            "1. 💰 PM-KISAN     → ₹6000/year (3 instalments)\n"
            "2. 🛡️ PMFBY        → Crop insurance at 1.5–2% premium\n"
            "3. 🏦 KCC          → Loan ₹3L at 4% interest\n"
            "4. 🚜 SMAM         → 25–50% machinery subsidy\n"
            "5. 💧 PMKSY        → 55% drip irrigation subsidy\n"
            "6. 🌱 Soil Card    → Free soil testing\n"
            "7. 🌾 eNAM         → Online mandi access\n\n"
            "Use 🏛️ Scheme Matcher in AI Tools to find ALL schemes you qualify for!"
        ),
        (
            "📋 How to apply for PM-KISAN:\n"
            "1. Visit pmkisan.gov.in\n"
            "2. Click 'Farmer Corner'\n"
            "3. Enter Aadhaar + land + bank details\n"
            "4. Submit at CSC or online\n"
            "5. ₹2000 credited every 4 months ✅\n\n"
            "For PMFBY crop insurance → contact your bank "
            "before crop sowing deadline!"
        ),
    ],

    "equipment_rental": [
        (
            "🚜 Equipment available on AgroNexus:\n"
            "• Tractor          : ₹200–400 /hr\n"
            "• Combine Harvester: ₹500–800 /hr\n"
            "• Sprayer          : ₹150–250 /hr\n"
            "• CRM Machine      : ₹300–500 /hr\n"
            "• Seeder           : ₹200–350 /hr\n"
            "• Rotavator        : ₹250–400 /hr\n\n"
            "Pay per hour — no full-day charges! "
            "→ Check 🚜 Equipment Rental in the sidebar!"
        ),
        (
            "💡 Equipment rental tips:\n"
            "• Book 1–2 days in advance during peak season\n"
            "• Compare rates from multiple owners\n"
            "• SMAM scheme gives 50% subsidy if you BUY equipment\n"
            "• GPS-tracked machines for safety\n"
            "• CRM machine turns crop residue into soil nutrients!\n\n"
            "Go to Equipment Rental page to book now!"
        ),
    ],

    "selling_crops": [
        (
            "🛒 Best ways to sell your crops:\n\n"
            "1. AgroNexus Marketplace → Direct buyers, zero commission\n"
            "2. eNAM                  → Online mandi, transparent pricing\n"
            "3. FPO / Group selling   → Better bulk price negotiation\n"
            "4. Direct to processors  → For large quantities\n"
            "5. Export via APEDA      → Premium prices for quality crops\n\n"
            "To list → Marketplace → Add Listing. "
            "Reach 10,000+ buyers instantly!"
        ),
        (
            "💰 Tips to get maximum price:\n"
            "• Grade your crop A/B/C (Grade A = 20% more!)\n"
            "• Sell when quality is at peak\n"
            "• Use AI Price Predictor to time your sale\n"
            "• Join an FPO for bulk negotiation power\n"
            "• Good packaging increases buyer trust\n\n"
            "Use AI Quality Grader to check your crop grade before listing!"
        ),
    ],

    "weather": [
        (
            "🌤️ General weather advisory:\n"
            "• Temperature  : 24–32°C\n"
            "• Humidity     : 65–75%\n"
            "• Wind         : 12–18 km/h\n"
            "• Rain forecast: Moderate this week\n\n"
            "✅ Good for: Sowing Rabi crops, fertilizer application\n"
            "⚠️ Avoid: Pesticide spray on windy days\n\n"
            "For hyperlocal forecast → Meghdoot app or imd.gov.in"
        ),
        (
            "🌧️ Monsoon farming tips:\n"
            "• Ensure proper drainage to prevent waterlogging\n"
            "• Delay fertilizer before heavy rain (washes away)\n"
            "• Monitor for fungal disease — humidity raises risk\n"
            "• Ideal time for Kharif crops: Paddy, Maize, Soybean\n"
            "• Store harvested produce before rain arrives\n\n"
            "Download Meghdoot app for farm-specific weather alerts!"
        ),
    ],

    "soil_health": [
        (
            "🌱 Soil health essentials:\n"
            "• Ideal pH     : 6.0–7.0 for most crops\n"
            "• pH < 6       → Acidic → add agricultural lime\n"
            "• pH > 7.5     → Alkaline → add gypsum or sulphur\n"
            "• Organic matter < 0.5% → add compost urgently\n\n"
            "📋 Get FREE Soil Health Card:\n"
            "1. Collect soil sample (15 cm depth)\n"
            "2. Submit to nearest KVK or soil lab\n"
            "3. Get NPK + micronutrient report free\n"
            "4. Receive crop-wise fertilizer recommendation"
        ),
        (
            "🌍 Improve your soil naturally:\n"
            "• Add 10 tonnes/ha FYM every season\n"
            "• Green manuring with Dhaincha / Sunhemp\n"
            "• Vermicompost improves structure + biology\n"
            "• Don't burn crop residue — kills soil microbes!\n"
            "• Use CRM machine to incorporate stubble\n"
            "• Crop rotation breaks pest cycles\n\n"
            "Good soil = good yield. Invest in soil health first!"
        ),
    ],

    "loan_finance": [
        (
            "🏦 Farm loan options:\n\n"
            "1. Kisan Credit Card (KCC)\n"
            "   • Up to ₹3 lakh at 4% interest\n"
            "   • Revolving credit — use anytime\n"
            "   • Apply at SBI, PNB, Cooperative banks\n\n"
            "2. NABARD loans — land dev & irrigation\n"
            "3. MUDRA loan   — agri-processing units\n"
            "4. PM SVANidhi  — small vendor support\n\n"
            "💡 Repay on time → get 2% extra subvention = 2% effective interest!"
        ),
        (
            "💳 How to apply for KCC:\n"
            "1. Go to nearest bank (SBI / PNB / Co-op)\n"
            "2. Carry: Aadhaar, land records, passport photo\n"
            "3. Fill KCC application form\n"
            "4. Bank approves within 14 working days\n"
            "5. Get card with ₹3 lakh credit at 4% ✅\n\n"
            "⚠️ Repay before season ends to avoid higher interest charges!"
        ),
    ],

    "post_harvest": [
        (
            "📦 Storage guidelines:\n"
            "• 🍅 Tomato   : 10–12°C, lasts 2–3 weeks\n"
            "• 🧅 Onion    : Cure 2 weeks, cool & dry storage\n"
            "• 🥔 Potato   : Dark, cool, well-ventilated\n"
            "• 🌾 Wheat    : Moisture < 14%, hermetic bags\n"
            "• 🌶️ Chilli  : Sun-dry to 8% moisture\n"
            "• 🌽 Maize    : Dry to 12% moisture, sealed bags\n\n"
            "Cold storage subsidy available under NHB scheme!"
        ),
        (
            "🏭 Value addition ideas:\n"
            "• Tomato    → Puree, ketchup, sun-dried\n"
            "• Chilli    → Powder, paste, oleoresin\n"
            "• Turmeric  → Powder, extract, cosmetics\n"
            "• Groundnut → Oil, peanut butter, flour\n"
            "• Mango     → Pickle, pulp, amchur powder\n\n"
            "Value addition can increase income 2–3×!\n"
            "PMFME scheme gives 35% subsidy for food processing units."
        ),
    ],

    "greeting": [
        (
            "🌾 Namaste! I'm AgroBot — your AI farming assistant!\n\n"
            "I can help you with:\n"
            "• 💰 Crop prices & predictions\n"
            "• 🌱 Crop & fertilizer advice\n"
            "• 🐛 Pest & disease management\n"
            "• 🏛️ Government schemes\n"
            "• 🚜 Equipment rental\n"
            "• 🛒 Selling your crops\n"
            "• 🏦 Farm loans & finance\n"
            "• 💧 Irrigation & soil health\n\n"
            "What do you need help with today?"
        ),
        (
            "👋 Hello Farmer! Welcome to AgroNexus!\n\n"
            "Ask me anything about farming — prices, crops, pests, "
            "schemes, loans, weather or equipment.\n"
            "I'm here to help you grow better and earn more! 🌾"
        ),
    ],

    "thanks": [
        "🙏 Happy to help! Ask me anything else about farming anytime!",
        "😊 Glad I could help! Wishing you a great harvest season! 🌾",
        "🌱 You're welcome! Come back anytime for farming advice!",
        "👍 Anytime! Good luck with your crops! 🌾",
    ],
}


# ══════════════════════════════════════════════════════════════════
# 3.  ENTITY LISTS — used to personalise responses
# ══════════════════════════════════════════════════════════════════
CROP_NAMES = [
    'tomato', 'rice', 'wheat', 'onion', 'potato', 'cotton', 'soybean',
    'maize', 'groundnut', 'chilli', 'turmeric', 'garlic', 'ginger',
    'mustard', 'sunflower', 'sugarcane', 'banana', 'mango', 'jowar',
    'bajra', 'arhar', 'moong', 'urad', 'chana', 'ragi', 'lentil',
    'peas', 'cauliflower', 'cabbage', 'brinjal', 'cucumber', 'okra',
    'paddy', 'groundnut', 'sesame', 'safflower', 'cowpea',
]

STATES = [
    'tamil nadu', 'punjab', 'maharashtra', 'karnataka',
    'uttar pradesh', 'andhra pradesh', 'gujarat', 'rajasthan',
    'madhya pradesh', 'bihar', 'west bengal', 'odisha',
    'haryana', 'telangana', 'kerala', 'assam', 'jharkhand',
]

# ── per-crop price data ────────────────────────────────────────────
CROP_PRICES = {
    'Tomato':    ('₹25–32', '₹28', 'rising ↑'),
    'Rice':      ('₹22–28', '₹25', 'stable →'),
    'Wheat':     ('₹20–25', '₹22', 'rising ↑'),
    'Onion':     ('₹14–22', '₹18', 'falling ↓'),
    'Potato':    ('₹12–18', '₹15', 'stable →'),
    'Cotton':    ('₹60–70', '₹65', 'rising ↑'),
    'Chilli':    ('₹75–92', '₹82', 'rising ↑'),
    'Turmeric':  ('₹95–115','₹105','rising ↑'),
    'Soybean':   ('₹42–50', '₹46', 'stable →'),
    'Maize':     ('₹18–23', '₹20', 'stable →'),
    'Groundnut': ('₹50–62', '₹55', 'rising ↑'),
    'Sugarcane': ('₹3–4',   '₹3.5','stable →'),
    'Mustard':   ('₹48–58', '₹52', 'rising ↑'),
    'Garlic':    ('₹80–100','₹90', 'rising ↑'),
    'Ginger':    ('₹60–80', '₹70', 'stable →'),
}

# ── per-crop fertilizer guide ─────────────────────────────────────
CROP_FERTILIZERS = {
    'Tomato':    'N:P:K = 150:75:75 kg/ha. Split N in 3 doses. Calcium spray prevents blossom-end rot.',
    'Rice':      'N:P:K = 120:60:60 kg/ha. Apply Urea in 3 splits. Use ZnSO₄ 25 kg/ha if yellowing.',
    'Wheat':     'N:P:K = 120:60:40 kg/ha. Full P & K at sowing; split N in 2 doses.',
    'Cotton':    'N:P:K = 180:80:80 kg/ha. Boron spray at flowering improves boll setting.',
    'Maize':     'N:P:K = 180:60:40 kg/ha. Side-dress with Urea at knee-high stage.',
    'Onion':     'N:P:K = 100:50:50 kg/ha. Avoid excess N near harvest — poor storage.',
    'Sugarcane': 'N:P:K = 250:100:100 kg/ha. Apply in 3–4 splits + 25 t/ha FYM.',
    'Potato':    'N:P:K = 120:80:100 kg/ha. High potash improves tuber size and quality.',
    'Soybean':   'N:P:K = 20:80:40 kg/ha. Rhizobium seed treatment saves N cost.',
    'Groundnut': 'N:P:K = 20:60:40 kg/ha. Gypsum 400 kg/ha at pegging stage.',
}

# ── per-state crop recommendations ────────────────────────────────
STATE_CROPS = {
    'Tamil Nadu':       ['Rice', 'Banana', 'Sugarcane', 'Coconut', 'Groundnut', 'Turmeric'],
    'Punjab':           ['Wheat', 'Rice', 'Maize', 'Cotton', 'Sugarcane'],
    'Maharashtra':      ['Sugarcane', 'Cotton', 'Soybean', 'Onion', 'Grapes'],
    'Karnataka':        ['Rice', 'Ragi', 'Maize', 'Sugarcane', 'Coffee', 'Sunflower'],
    'Uttar Pradesh':    ['Wheat', 'Sugarcane', 'Rice', 'Potato', 'Mustard'],
    'Andhra Pradesh':   ['Rice', 'Chilli', 'Tobacco', 'Cotton', 'Groundnut'],
    'Gujarat':          ['Cotton', 'Groundnut', 'Wheat', 'Bajra', 'Tobacco'],
    'Rajasthan':        ['Bajra', 'Wheat', 'Mustard', 'Jowar', 'Guar'],
    'Madhya Pradesh':   ['Soybean', 'Wheat', 'Maize', 'Cotton', 'Arhar'],
    'Bihar':            ['Wheat', 'Rice', 'Maize', 'Lentil', 'Mustard'],
    'West Bengal':      ['Rice', 'Jute', 'Potato', 'Mustard', 'Tea'],
    'Odisha':           ['Rice', 'Maize', 'Groundnut', 'Sugarcane', 'Jute'],
    'Haryana':          ['Wheat', 'Rice', 'Cotton', 'Mustard', 'Sugarcane'],
    'Telangana':        ['Rice', 'Cotton', 'Maize', 'Chilli', 'Turmeric'],
    'Kerala':           ['Coconut', 'Rubber', 'Banana', 'Pepper', 'Cardamom'],
}


# ══════════════════════════════════════════════════════════════════
# 4.  ENTITY EXTRACTOR
# ══════════════════════════════════════════════════════════════════
def extract_entities(text: str) -> dict:
    text_lower = text.lower()
    entities   = {'crops': [], 'states': [], 'numbers': []}

    for crop in CROP_NAMES:
        if crop in text_lower:
            entities['crops'].append(crop)

    for state in STATES:
        if state in text_lower:
            entities['states'].append(state)

    entities['numbers'] = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', text)]

    return entities


# ══════════════════════════════════════════════════════════════════
# 5.  ML PIPELINE — TF-IDF  +  Logistic Regression
# ══════════════════════════════════════════════════════════════════
def _build_training_data():
    X, y = [], []
    for intent, examples in INTENT_DATA.items():
        for ex in examples:
            X.append(ex)
            y.append(intent)
    return X, y


def train_model():
    X, y = _build_training_data()

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),    # unigrams, bigrams, trigrams
            min_df=1,
            max_features=8000,
            sublinear_tf=True,
            strip_accents='unicode',
            analyzer='word',
        )),
        ('clf', LogisticRegression(
            max_iter=1000,
            C=5.0,
            class_weight='balanced',
            solver='lbfgs',
            multi_class='multinomial',
        )),
    ])

    pipeline.fit(X, y)
    print(f"[AgroBot] Trained on {len(X)} examples | {len(INTENT_DATA)} intents")
    return pipeline


# ══════════════════════════════════════════════════════════════════
# 6.  CHATBOT CLASS
# ══════════════════════════════════════════════════════════════════
class AgroBot:

    CONFIDENCE_THRESHOLD = 0.22   # below this → use fallback

    def __init__(self):
        self.model   = train_model()
        self.context = {}          # session_id → last_intent

    # ── intent prediction ──────────────────────────────────────────
    def predict_intent(self, text: str):
        proba      = self.model.predict_proba([text])[0]
        top_idx    = int(np.argmax(proba))
        confidence = float(proba[top_idx])
        intent     = self.model.classes_[top_idx]
        return intent, confidence

    # ── main entry point ───────────────────────────────────────────
    def get_response(self, message: str, session_id: str = 'default') -> str:
        message = message.strip()
        if not message:
            return "Please type a farming question! 🌾"

        intent, confidence = self.predict_intent(message)
        entities           = extract_entities(message)

        # low-confidence fallback
        if confidence < self.CONFIDENCE_THRESHOLD:
            return self._fallback(message, entities)

        # save context
        self.context[session_id] = intent

        # ── personalised responses ─────────────────────────────────
        if entities['crops']:
            crop = entities['crops'][0].capitalize()

            if intent == 'crop_price':
                return self._crop_price_response(crop)

            if intent == 'fertilizer_advice':
                return self._fertilizer_response(crop)

            if intent == 'pest_disease':
                return self._pest_response(crop)

            if intent == 'price_prediction':
                return self._prediction_response(crop)

        if entities['states'] and intent == 'crop_recommendation':
            state = entities['states'][0].title()
            return self._state_crops_response(state)

        # ── generic intent response ────────────────────────────────
        replies = RESPONSES.get(intent)
        if not replies:
            return self._fallback(message, entities)

        return random.choice(replies)

    # ── personalised builders ──────────────────────────────────────
    def _crop_price_response(self, crop: str) -> str:
        p = CROP_PRICES.get(crop)
        if p:
            return (
                f"📊 {crop} Price Today:\n"
                f"  Market range : {p[0]} /kg\n"
                f"  Average      : {p[1]} /kg\n"
                f"  Trend        : {p[2]}\n\n"
                f"💡 Use AI Price Prediction for a 7-day forecast!"
            )
        return (
            f"📊 I don't have live data for {crop} right now.\n"
            f"Use the 📈 AI Price Predictor for the latest forecast, "
            f"or check enam.gov.in for current mandi rates."
        )

    def _fertilizer_response(self, crop: str) -> str:
        tip = CROP_FERTILIZERS.get(crop)
        if tip:
            return (
                f"🧪 Fertilizer guide for {crop}:\n{tip}\n\n"
                f"⚠️ Always do a soil test first for precise dosing. "
                f"Get a FREE Soil Health Card at your nearest KVK!"
            )
        return (
            f"🧪 For {crop}, a general recommendation is "
            f"N:P:K = 120:60:40 kg/ha.\n"
            f"Get your FREE Soil Health Card for a crop-specific plan!"
        )

    def _pest_response(self, crop: str) -> str:
        guides = {
            'Tomato':  'Leaf curl → control whitefly with neem oil. Fruit borer → Spinosad spray. Early blight → Mancozeb.',
            'Rice':    'Blast → Tricyclazole spray. BPH → drain field + Imidacloprid. Stem borer → Carbofuran 3G.',
            'Wheat':   'Rust → Propiconazole. Aphids → Dimethoate. Loose smut → seed treatment with Carboxin.',
            'Cotton':  'Bollworm → BT spray + pheromone traps. Whitefly → Yellow sticky traps + neem oil.',
            'Onion':   'Thrips → Blue sticky traps + Spinosad. Purple blotch → Mancozeb spray.',
            'Potato':  'Late blight → Metalaxyl spray at first sign. Aphids → Imidacloprid seed treatment.',
            'Chilli':  'Mite → Dicofol spray. Thrips → Spinosad. Anthracnose → Copper oxychloride.',
            'Maize':   'Fall armyworm → Emamectin benzoate in whorl. Downy mildew → Metalaxyl seed treatment.',
        }
        tip = guides.get(crop, f'Use IPM approach for {crop}. Neem oil works for most soft-bodied insects. Consult local KVK for disease-specific fungicides.')
        return (
            f"🐛 Pest & Disease guide for {crop}:\n{tip}\n\n"
            f"💡 For accurate diagnosis, upload a photo in the Quality Grader!"
        )

    def _prediction_response(self, crop: str) -> str:
        p = CROP_PRICES.get(crop)
        if p:
            trend = p[2]
            advice = (
                "Good time to hold stock for 2–3 more days."
                if 'rising' in trend
                else "Consider selling soon before further decline."
                if 'falling' in trend
                else "Market is stable — sell when ready."
            )
            return (
                f"📈 {crop} price forecast:\n"
                f"  Current avg : {p[1]} /kg\n"
                f"  Trend       : {trend}\n"
                f"  Advice      : {advice}\n\n"
                f"For a precise 7-day ML forecast → AI Tools → Price Prediction!"
            )
        return (
            f"🤖 Use AI Tools → Price Prediction for a 7-day ML forecast for {crop}. "
            f"It uses historical mandi data + seasonal patterns!"
        )

    def _state_crops_response(self, state: str) -> str:
        crops = STATE_CROPS.get(state, ['Wheat', 'Rice', 'Maize', 'Vegetables'])
        crop_list = '\n'.join([f"  {i+1}. {c}" for i, c in enumerate(crops)])
        return (
            f"🌾 Top crops for {state}:\n{crop_list}\n\n"
            f"💡 Use the Crop Advisor in AI Tools for season + soil specific advice!"
        )

    # ── fallback ───────────────────────────────────────────────────
    def _fallback(self, message: str, entities: dict) -> str:
        if entities['crops']:
            crop = entities['crops'][0].capitalize()
            return (
                f"🌱 You mentioned {crop}. What would you like to know?\n"
                f"• Price of {crop}\n"
                f"• Fertilizer for {crop}\n"
                f"• Pest control for {crop}\n"
                f"• Best time to sell {crop}"
            )

        suggestions = [
            (
                "🤔 I didn't quite get that. Try asking:\n"
                "• 'What is tomato price today?'\n"
                "• 'Which crop should I grow in summer?'\n"
                "• 'How to treat pest on wheat?'\n"
                "• 'Government schemes for farmers'\n"
                "• 'How to get KCC loan?'"
            ),
            (
                "🌾 I can help with:\n"
                "Crop prices · Price predictions · Fertilizer advice\n"
                "Pest control · Irrigation · Govt schemes · Loans\n"
                "Equipment rental · Selling crops · Weather\n\n"
                "Please rephrase your question!"
            ),
        ]
        return random.choice(suggestions)


# ══════════════════════════════════════════════════════════════════
# 7.  SINGLETON — one model instance shared across all requests
# ══════════════════════════════════════════════════════════════════
_bot_instance = None

def get_bot() -> AgroBot:
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = AgroBot()
    return _bot_instance


# ══════════════════════════════════════════════════════════════════
# 8.  PUBLIC API — called from app.py
# ══════════════════════════════════════════════════════════════════
def chatbot_response(message: str, session_id: str = 'default') -> str:
    """
    Called from Flask route:

        from ml_models.agri_chatbot import chatbot_response
        response = chatbot_response(message, session_id)
    """
    return get_bot().get_response(message, session_id)


# ══════════════════════════════════════════════════════════════════
# 9.  STANDALONE TEST  —  python agri_chatbot.py
# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    bot = AgroBot()

    AUTO_TESTS = [
        "what is the price of tomato today",
        "which crop should I grow in Tamil Nadu",
        "fertilizer for rice crop",
        "how to treat pest on wheat",
        "government schemes for farmers",
        "how to rent a tractor",
        "will onion price increase next week",
        "how to store potatoes after harvest",
        "how to get KCC loan",
        "drip irrigation subsidy",
        "hello",
        "thank you",
        "random gibberish xyz abc",
    ]

    print("=" * 60)
    print("  AgroBot NLP — Auto Test")
    print("=" * 60)
    for q in AUTO_TESTS:
        intent, conf = bot.predict_intent(q)
        resp = bot.get_response(q)
        print(f"\n❓ {q}")
        print(f"   Intent     : {intent}  ({conf*100:.1f}%)")
        print(f"   Response   : {resp[:90]}{'...' if len(resp)>90 else ''}")

    print("\n" + "=" * 60)
    print("  Interactive Mode  (type 'quit' to exit)")
    print("=" * 60)
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ('quit', 'exit', 'bye', 'q'):
            print("AgroBot: Goodbye! Happy farming! 🌾")
            break
        if user_input:
            print(f"AgroBot: {bot.get_response(user_input)}")