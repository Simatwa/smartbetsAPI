#!usr/bin/env python3
from smartbets_API.predictor import predictor

teams = {
    1: "Manchester City",  # 1 for home-team
    2: "Liverpool",  # 2 for away-team
}

# Instantiating predictor
predict = predictor()

# Using predictorD object to handle teams (Dictionary data-type)
predictions = predict.predictorD(teams)

# Display info
print(predictions)

# Output
# {'g': 8.0, 'gg': 65.0, 'ov15': 60.0, 'ov25': 45.0, 'ov35': 30.0, 'choice': 56.16, 'result': '1', 'pick': 'gg'}
