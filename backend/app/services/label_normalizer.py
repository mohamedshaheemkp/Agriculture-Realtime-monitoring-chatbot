import json
import os
import logging

# Module-level logger (standard Python logging, no external framework deps)
logger = logging.getLogger(__name__)

# Default hardcoded map as a fallback if file load fails
DEFAULT_LABEL_MAP = {
    "Tomato Early blight leaf": "Early Blight",
    "Tomato mold leaf": "Leaf Mold",
    "Tomato healthy leaf": "Healthy",
    "Tomato Septoria leaf spot": "Septoria Leaf Spot",
    "Tomato Two-spotted spider mite": "Spider Mites",
    "Tomato Target Spot": "Target Spot",
    "Tomato Yellow Leaf Curl Virus": "Yellow Leaf Curl Virus",
    "Tomato Mosaic virus": "Mosaic Virus"
}

class LabelNormalizer:
    """
    Central Service for normalizing raw model labels (e.g., 'Tomato_Early_blight') 
    into user-friendly display names (e.g., 'Early Blight').
    
    Why Centralized?
    - Ensures consistency across Chatbot, Logs, Databases, and Frontend.
    - Decouples model output naming from user interface naming.
    
    Configuration:
    - New labels should be added to `backend/config/label_map.json`.
    - No code changes are required to support new classes if added to JSON.
    """
    def __init__(self, config_path="label_map.json"):
        self.label_map = DEFAULT_LABEL_MAP.copy()
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        """
        Attempts to load label mappings from a JSON configuration file.
        Updates self.label_map with any entries found.
        """
        # Look for the config file relative to the project root or current directory
        # We try a few common locations if a relative path is given
        possible_paths = [
            self.config_path,
            os.path.join("backend", "config", self.config_path),
            os.path.join(os.path.dirname(__file__), "..", "..", "config", self.config_path)
        ]

        loaded = False
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        config_data = json.load(f)
                        # Assume config structure is simple dict or has a 'labels' key
                        new_labels = config_data.get('labels', config_data)
                        if isinstance(new_labels, dict):
                            self.label_map.update(new_labels)
                            logging.info(f"Loaded label mappings from {path}")
                            loaded = True
                            break
                except Exception as e:
                    logging.warning(f"Failed to load label config from {path}: {e}")
        
        if not loaded:
            logging.debug("Using default hardcoded label mappings.")

    def normalize(self, raw_label: str) -> str:
        """
        Converts a raw YOLO model label into a clean, human-readable format.
        Gracefully falls back to the original label if no mapping exists.
        """
        if not raw_label:
            return "Unknown"
            
        # 1. Check exact match
        if raw_label in self.label_map:
            return self.label_map[raw_label]
        
        # 2. Check case-insensitive match (performance optimization: cache this if list is huge)
        raw_lower = raw_label.lower()
        for key, value in self.label_map.items():
            if key.lower() == raw_lower:
                return value
                
        # 3. Fallback: Return original label unchanged (Backward Compatibility)
        return raw_label

# Singleton instance for easy import
normalizer = LabelNormalizer()

# Expose the functional simplified API
def normalize_label(raw_label: str) -> str:
    return normalizer.normalize(raw_label)
