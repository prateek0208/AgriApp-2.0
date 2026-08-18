import joblib
from core.paths import get_path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_predicted_price(crop_name: str, n: float, p: float, k: float,
                        ph: float, rainfall: float, acres: float) -> float:
    """
    Uses the trained ML price model to predict investment cost for a crop.

    Args:
        crop_name: Predicted crop (used for logging context)
        n, p, k: Soil nutrient values in ppm
        ph: Soil pH
        rainfall: Rainfall in mm
        acres: Farm size in acres

    Returns:
        Predicted price as float, or 0.0 on any failure.
    """
    try:
        model = joblib.load(get_path('models', 'price_model.pkl'))

        # Feature order MUST match training dataset column order
        input_data = pd.DataFrame(
            [[n, p, k, ph, rainfall, acres]],
            columns=['N', 'P', 'K', 'ph', 'rainfall', 'acres']
        )

        prediction = model.predict(input_data)[0]
        return round(float(prediction), 2)

    except FileNotFoundError:
        logger.error("price_model.pkl not found. Make sure it's in the project root.")
        return 0.0
    except ValueError as e:
        logger.error(f"Feature mismatch in price model input: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error in price prediction for crop '{crop_name}': {e}")
        return 0.0