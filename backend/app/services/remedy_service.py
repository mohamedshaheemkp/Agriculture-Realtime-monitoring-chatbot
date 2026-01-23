
import logging

logger = logging.getLogger(__name__)

class RemedyService:
    """
    A rule-based engine to determine the best agricultural remedy 
    based on disease detection and current weather context.
    
    Design Principles:
    - Explainable: Returns 'reasoning' for every decision.
    - No Black Box: Logic is transparently defined in the generic rules.
    - Extensible: Rules are separated from logic in the _knowledge_base.
    """

    def __init__(self):
        # In a real app, this could be loaded from a JSON/YAML file or Database.
        self._knowledge_base = {
            "default": {
                "action": "Monitor plant health closely.",
                "reason": "No specific specific remedy found for this detection."
            },
            "potato_early_blight": {
                "type": "fungal",
                "standard_action": "Apply Copper-based Fungicide (e.g., Mancozeb).",
                "organic_action": "Remove infected leaves and apply Neem Oil.",
                "severity": "high"
            },
            "tomato_early_blight": {
                "type": "fungal",
                "standard_action": "Apply Copper-based Fungicide.",
                "organic_action": "Prune lower leaves and improve airflow.",
                "severity": "medium"
            },
            "tomato_late_blight": {
                "type": "fungal",
                "standard_action": "Apply broad-spectrum fungicide (Chlorothalonil).",
                "organic_action": "Destroy infected plants immediately to prevent spread.",
                "severity": "critical"
            },
            "tomato_leaf_mold": {
                 "type": "fungal",
                 "standard_action": "Apply fungicide specifically for leaf mold.",
                 "organic_action": "Reduce humidity and improve ventilation.",
                 "severity": "medium"
            },
            "corn_common_rust": {
                "type": "fungal",
                "standard_action": "Apply fungicide early.",
                "organic_action": "Plant resistant varieties next season.",
                "severity": "medium"
            },
            # Pest Examples
            "aphids": {
                "type": "pest",
                "standard_action": "Apply Insecticidal Soap.",
                "organic_action": "Release Ladybugs or spray Neem Oil.",
                "severity": "medium"
            }
        }

    def recommend(self, detection_label: str, weather_context: dict) -> dict:
        """
        Determines the remedy and reasoning based on inputs.
        
        Args:
            detection_label (str): The raw label from the vision model (e.g., "Tomato_Early_Blight").
            weather_context (dict): Weather data containing keys like 'condition', 'wind_kph', 'humidity'.
                                    Example: {'condition': 'Rain', 'wind_kph': 15, 'humidity': 85}
        
        Returns:
            dict: { "remedy": str, "reasoning": str, "alert_level": str }
        """
        
        # 1. Normalize Input
        key = detection_label.lower().replace(" ", "_")
        
        # Fallback for complex keys like "Tomato_Early_Blight" -> try partial matches if direct specific key not found?
        # For this implementation, we assume basic normalization maps to keys.
        # If not specific match, try to find a generic fallback based on keywords.
        rule = self._knowledge_base.get(key)
        
        if not rule:
            # Try finding a partial match in keys
            for k, v in self._knowledge_base.items():
                if k in key:
                    rule = v
                    break
        
        if not rule:
            return {
                "remedy": "Conduct detailed manual inspection.",
                "reasoning": f"No specific rule found for '{detection_label}'.",
                "alert_level": "Info"
            }
            
        # 2. Extract Context Variables
        is_raining = "rain" in str(weather_context.get("condition", "")).lower()
        wind_speed = weather_context.get("wind_kph", 0)
        humidity = weather_context.get("humidity_pct", 0) # Assumed key from weather_service
        
        # 3. Apply Weather Constraints (The "Meta-Rules")
        
        # Rule A: Rain Constraint
        # Logic: Most treatments (especially sprays) wash off in rain.
        if is_raining:
            return {
                "remedy": "Delay treatment until rain stops.",
                "reasoning": f"Identified needs for {rule.get('standard_action', 'treatment')}, but active rain will wash away chemical/organic applications, rendering them ineffective.",
                "alert_level": "Warning"
            }
            
        # Rule B: Wind Constraint
        # Logic: High wind causes chemical drift, wasting product and harming environment.
        if wind_speed > 15: # Threshold of 15 kph
            return {
                "remedy": "Delay spraying/treatment due to high wind.",
                "reasoning": f"Wind speed is {wind_speed} km/h. Spraying now risks chemical drift to non-target areas.",
                "alert_level": "Warning"
            }

        # Rule C: Fungal Logic (Humidity)
        # Logic: Fungi thrive in high humidity. Intervention is more urgent.
        if rule.get("type") == "fungal" and humidity > 80:
             return {
                "remedy": f"URGENT: {rule['standard_action']} (Apply Rain-fast format if available)",
                "reasoning": f"High humidity ({humidity}%) is accelerating fungal growth. Immediate action required to prevent rapid spread.",
                "alert_level": "Critical"
             }

        # 4. Default Recommendation
        # If no constraints block action, recommend the standard action.
        return {
            "remedy": rule["standard_action"],
            "reasoning": f"Weather conditions are favorable (No rain, Wind < 15km/h). {detection_label} matches standard protocol.",
            "alert_level": "Actionable"
        }

remedy_service = RemedyService()
