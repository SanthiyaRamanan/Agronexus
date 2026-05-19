"""
Crop Quality Grader - Grades crop quality based on parameters
"""

QUALITY_STANDARDS = {
    'tomato':    {'color': 8, 'size_uniformity': 7, 'firmness': 8, 'defect_rate': 2},
    'rice':      {'moisture': 14, 'broken_percent': 5, 'purity': 95, 'foreign_matter': 1},
    'wheat':     {'moisture': 13, 'protein_percent': 11, 'gluten': 28, 'broken': 2},
    'onion':     {'moisture': 85, 'pungency': 7, 'size': 6, 'defect_rate': 3},
    'potato':    {'size': 7, 'dry_matter': 20, 'defect_rate': 3, 'sprouting': 0},
    'default':   {'quality_score': 70, 'moisture': 13, 'purity': 90, 'defect_rate': 5},
}

def grade_crop_quality(crop: str, params: dict) -> dict:
    """
    Grade crop quality as A/B/C with score and recommendations.
    In production: CNN model on crop images for visual grading.
    """
    import random
    crop_lower = crop.lower()
    standards = QUALITY_STANDARDS.get(crop_lower, QUALITY_STANDARDS['default'])
    score = random.randint(55, 97)

    if score >= 85:
        grade = 'A'
        grade_label = 'Premium Quality'
        price_multiplier = 1.20
        color = '#2d9e6b'
        recommendations = [
            'Excellent quality! You can fetch premium market prices.',
            'Pack in ventilated crates to maintain freshness.',
            'Target export markets and premium retailers.',
        ]
    elif score >= 65:
        grade = 'B'
        grade_label = 'Standard Quality'
        price_multiplier = 1.00
        color = '#f0a500'
        recommendations = [
            'Good quality suitable for wholesale markets.',
            'Ensure proper cold-chain storage during transport.',
            'Can be upgraded to Grade A with better post-harvest handling.',
        ]
    else:
        grade = 'C'
        grade_label = 'Below Standard'
        price_multiplier = 0.75
        color = '#e05252'
        recommendations = [
            'Consider processing into value-added products.',
            'Improve harvesting timing and post-harvest handling next season.',
            'Check for pest/disease management gaps.',
        ]

    return {
        'grade': grade,
        'grade_label': grade_label,
        'score': score,
        'color': color,
        'price_multiplier': price_multiplier,
        'price_impact': f'+{int((price_multiplier-1)*100)}%' if price_multiplier >= 1 else f'{int((price_multiplier-1)*100)}%',
        'recommendations': recommendations,
        'parameters_analyzed': list(standards.keys()),
    }
