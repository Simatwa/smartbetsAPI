__version__ = "1.2.9"
__author__ = "Smartwa Caleb"
from .bet_at_rest_api_level import predictor as rest_api
from .predictor import predictor

__all__ = [
    "predictor",
    "rest_api",
]
