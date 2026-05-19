"""
Government Scheme Matcher - Matches farmers to eligible government schemes
"""

ALL_SCHEMES = [
    {
        'name': 'PM-KISAN',
        'description': 'Direct income support of ₹6000/year to small and marginal farmers',
        'benefits': '₹6,000 per year (3 installments of ₹2,000)',
        'eligibility': 'Land-holding farmers with cultivable land',
        'max_land': 999,  # acres (no limit)
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://pmkisan.gov.in',
        'priority': 10,
    },
    {
        'name': 'PMFBY - Crop Insurance',
        'description': 'Crop insurance to protect against crop loss due to natural calamities',
        'benefits': 'Insurance cover at 1.5% (Kharif) and 2% (Rabi) premium',
        'eligibility': 'All farmers including sharecroppers and tenant farmers',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://pmfby.gov.in',
        'priority': 9,
    },
    {
        'name': 'Kisan Credit Card (KCC)',
        'description': 'Revolving credit for farmers at subsidized interest rates',
        'benefits': 'Loan up to ₹3 lakh at 4% interest (after 2% subvention)',
        'eligibility': 'Farmers, sharecroppers, self-help groups',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://www.nabard.org/kcc',
        'priority': 8,
    },
    {
        'name': 'SMAM - Equipment Subsidy',
        'description': 'Subsidy on purchase of agricultural machinery and equipment',
        'benefits': '25% to 50% subsidy on farm machinery',
        'eligibility': 'Small and marginal farmers (land < 5 acres preferred)',
        'max_land': 10,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://agrimachinery.nic.in',
        'priority': 7,
    },
    {
        'name': 'National Food Security Mission',
        'description': 'Increasing production of rice, wheat, pulses, coarse cereals',
        'benefits': 'Free seeds, fertilizer subsidies, technical support',
        'eligibility': 'Farmers growing rice, wheat, pulses, coarse cereals',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['rice', 'wheat', 'pulses', 'maize', 'jowar', 'bajra'],
        'url': 'https://nfsm.gov.in',
        'priority': 6,
    },
    {
        'name': 'Soil Health Card Scheme',
        'description': 'Free soil health testing and recommendations',
        'benefits': 'Free soil testing kit + crop-wise fertilizer recommendation',
        'eligibility': 'All farmers',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://soilhealth.dac.gov.in',
        'priority': 5,
    },
    {
        'name': 'SC/ST Special Agriculture Package',
        'description': 'Special support package for SC/ST farmer communities',
        'benefits': 'Enhanced subsidy (up to 75%) on inputs and equipment',
        'eligibility': 'SC/ST category farmers only',
        'max_land': 999,
        'categories': ['SC', 'ST'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://agricoop.nic.in',
        'priority': 10,
    },
    {
        'name': 'Pradhan Mantri Krishi Sinchai Yojana',
        'description': 'Water to every field, more crop per drop',
        'benefits': 'Drip/sprinkler irrigation subsidy up to 55%',
        'eligibility': 'All farmers, priority to water-scarce regions',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://pmksy.gov.in',
        'priority': 7,
    },
    {
        'name': 'Organic Farming Scheme (Paramparagat Krishi Vikas Yojana)',
        'description': 'Promote organic farming clusters',
        'benefits': '₹50,000/hectare over 3 years for organic inputs, certification, marketing',
        'eligibility': 'Farmer groups (min 20 farmers, 20 acres cluster)',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://pgsindia-ncof.gov.in',
        'priority': 6,
    },
    {
        'name': 'eNAM - Market Linkage',
        'description': 'Electronic National Agriculture Market for pan-India trading',
        'benefits': 'Access to 1000+ mandis, transparent price discovery, online payment',
        'eligibility': 'Farmers registered with local APMC',
        'max_land': 999,
        'categories': ['All'],
        'states': ['All'],
        'crops': ['All'],
        'url': 'https://enam.gov.in',
        'priority': 8,
    },
]

def match_schemes(state: str, crop: str, land_size: float, category: str) -> list:
    """Match farmer profile to eligible government schemes."""
    matched = []
    crop_lower = crop.lower() if crop else ''
    state_lower = state.lower() if state else ''
    cat = category.upper() if category else 'General'

    for scheme in ALL_SCHEMES:
        # Check land size
        if land_size > scheme['max_land']:
            continue

        # Check category
        if 'All' not in scheme['categories'] and cat not in scheme['categories']:
            continue

        # Check crop match
        if 'All' not in scheme['crops']:
            if not any(c in crop_lower for c in scheme['crops']):
                continue

        # Check state
        if 'All' not in scheme['states'] and state_lower not in [s.lower() for s in scheme['states']]:
            continue

        matched.append({
            'name': scheme['name'],
            'description': scheme['description'],
            'benefits': scheme['benefits'],
            'eligibility': scheme['eligibility'],
            'url': scheme['url'],
            'priority': scheme['priority'],
        })

    # Sort by priority
    matched.sort(key=lambda x: x['priority'], reverse=True)
    return matched
