
# Mapping of diseases (normalized names) to their characteristic symptoms/features.
DISEASE_FEATURES = {
    "Early Blight": [
        "Small black or brown spots on leaves",
        "Yellowing around lesions",
        "Premature leaf drop"
    ],
    "Leaf Mold": [
        "Pale green or yellow spots on upper leaf surfaces",
        "Olive-green to brown velvety mold on undersides",
        "Leaves curl and wither"
    ],
    "Septoria Leaf Spot": [
        "Circular spots with gray centers and dark borders",
        "Small black fruiting bodies in the center of spots",
        "Lower leaves affected first"
    ],
    "Spider Mites": [
        "Tiny yellow or white speckles (stippling) on leaves",
        "Fine webbing on plants",
        "Leaves turn yellow, bronze, and curl"
    ],
    "Target Spot": [
        "Target-shaped spots with concentric rings",
        "Dark brown necrotic areas",
        "Leaf yellowing"
    ],
    "Yellow Leaf Curl Virus": [
        "Leaves curl upward and turn yellow at edges",
        "Stunted plant growth",
        "Flower drop"
    ],
    "Mosaic Virus": [
        "Mottled light and dark green pattern on leaves",
        "Leaves crinkled or distorted",
        "Stunted growth"
    ],
    "Blight": [ 
        "General term for rapid weathering/death of leaves", 
        "Discoloration and lesions" 
    ],
    "Aphids": [
        "Tiny soft-bodied insects",
        "Sooty mold growth on honeydew",
        "Yellowing and distorted leaves"
    ],
    "Healthy": [
        "Vibrant green leaves",
        "No visible lesions or spots",
        "Normal growth pattern"
    ]
}

def get_disease_features(disease_name):
    """
    Returns a list of features/symptoms for a given disease name.
    Returns an empty list if details are unavailable.
    """
    if not disease_name:
        return []
        
    return DISEASE_FEATURES.get(disease_name, [])
