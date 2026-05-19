"""
Crop Advisor - Recommends best crops based on location, season, and soil type
"""

CROP_RECOMMENDATIONS = {
    'kharif': {
        'sandy':  ['groundnut', 'pearl millet', 'sesame', 'moong'],
        'clay':   ['paddy', 'sugarcane', 'jute', 'cotton'],
        'loamy':  ['maize', 'soybean', 'arhar', 'sunflower'],
        'red':    ['groundnut', 'cotton', 'chilli', 'tobacco'],
        'black':  ['cotton', 'soybean', 'jowar', 'sunflower'],
    },
    'rabi': {
        'sandy':  ['mustard', 'barley', 'chickpea', 'linseed'],
        'clay':   ['wheat', 'sugarcane', 'peas', 'lentil'],
        'loamy':  ['wheat', 'mustard', 'potato', 'onion'],
        'red':    ['wheat', 'chickpea', 'linseed', 'safflower'],
        'black':  ['wheat', 'chickpea', 'sorghum', 'linseed'],
    },
    'zaid': {
        'sandy':  ['watermelon', 'muskmelon', 'cucumber', 'pumpkin'],
        'clay':   ['moong', 'urad', 'cowpea', 'bitter gourd'],
        'loamy':  ['moong', 'sesame', 'sunflower', 'fodder crops'],
        'red':    ['groundnut', 'watermelon', 'vegetables'],
        'black':  ['cotton', 'jowar', 'vegetables'],
    }
}

LOCATION_BONUS = {
    'tamil nadu':   ['rice', 'banana', 'sugarcane', 'coconut', 'groundnut'],
    'punjab':       ['wheat', 'rice', 'maize', 'cotton', 'sugarcane'],
    'maharashtra':  ['sugarcane', 'cotton', 'soybean', 'onion', 'grapes'],
    'karnataka':    ['rice', 'ragi', 'maize', 'sugarcane', 'coffee'],
    'up':           ['wheat', 'sugarcane', 'rice', 'potato', 'mustard'],
    'andhra pradesh': ['rice', 'chilli', 'tobacco', 'cotton', 'groundnut'],
    'gujarat':      ['cotton', 'groundnut', 'tobacco', 'wheat', 'bajra'],
    'rajasthan':    ['bajra', 'wheat', 'mustard', 'jowar', 'guar'],
    'mp':           ['soybean', 'wheat', 'maize', 'cotton', 'arhar'],
    'bihar':        ['wheat', 'rice', 'maize', 'lentil', 'mustard'],
}

SOIL_TIPS = {
    'sandy':  'Sandy soil drains quickly. Use drip irrigation and add organic matter. Good for root crops.',
    'clay':   'Clay soil retains moisture well. Ensure proper drainage. Excellent for rice and sugarcane.',
    'loamy':  'Loamy soil is ideal for most crops. Maintain organic matter. High water retention capacity.',
    'red':    'Red soil is low in nitrogen. Add compost regularly. Ideal for millets and pulses.',
    'black':  'Black (cotton) soil retains moisture long. Avoid waterlogging. Excellent for cotton and wheat.',
}


def get_crop_advice(location: str, season: str, soil_type: str) -> dict:
    """
    Return crop recommendations based on inputs.
    In production: trained Decision Tree / Random Forest on agro-climatic data.
    """
    season_key = season.lower() if season.lower() in CROP_RECOMMENDATIONS else 'kharif'
    soil_key   = soil_type.lower() if soil_type.lower() in SOIL_TIPS else 'loamy'
    location_key = location.lower()

    recommended = CROP_RECOMMENDATIONS[season_key].get(soil_key, ['wheat', 'rice', 'maize'])

    # Add location-specific crops
    for loc, crops in LOCATION_BONUS.items():
        if loc in location_key:
            for c in crops[:2]:
                if c not in recommended:
                    recommended.insert(0, c)
            break

    recommended = recommended[:6]

    soil_tip = SOIL_TIPS.get(soil_key, 'Maintain soil health with organic compost and proper irrigation.')

    watering = {
        'kharif': 'Monsoon season — natural rainfall usually sufficient. Monitor for overwatering.',
        'rabi':   'Winter season — irrigate every 15-20 days. Watch for frost.',
        'zaid':   'Summer season — irrigate every 7-10 days. Use mulching to retain moisture.',
    }.get(season_key, 'Irrigate as per crop requirement.')

    return {
        'recommended_crops': recommended,
        'soil_tip': soil_tip,
        'watering_advice': watering,
        'season': season_key,
        'fertilizer_tip': 'Apply NPK 120:60:40 kg/ha for best results. Consider soil testing first.',
        'expected_yield': 'With proper care, expect 20-30% higher yield than district average.'
    }
