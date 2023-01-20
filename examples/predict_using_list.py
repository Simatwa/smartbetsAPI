#!usr/bin/env python3
from smartbets_API.predictor import predictor

teams = [
    "Napoli",  # Home team (index [0])
    "AC Milan",  # Away team (index [1])
]
# Instantiating predictor
predict = predictor()

# Using predictorL object to handle teams (List data-type)
predictions = predict.predictorL(teams)

# Display info
print(predictions)

#Output
#{'g': 8.0, 'gg': 65.0, 'ov15': 70.0, 'ov25': 40.0, 'ov35': 30.0, 'choice': 60.0, 'result': '2', 'pick': 'ov15'}