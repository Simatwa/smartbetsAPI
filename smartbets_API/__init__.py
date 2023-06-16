__version__ = "1.1.4"
__author__ = "Smartwa Caleb"
from .bet_at_api_level import predictor as rest_api
from .predictor import predictor

__all__=[
    'predictor',
    'rest_api',
]