from requests import Session
from json import loads
from os import path


class predictor:
    def __init__(self, api_url: str, token: str):
        self.url = api_url
        self.session = Session()
        self.session.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    # Interacts with the api
    def __requester(self, **kwargs):
        try:
            response = self.session.post(**kwargs)
        except Exception as e:
            resp = {"succeed": False, "feedback": e, "status_code": 0}
        else:
            resp = {
                "succeed": True,
                "feedback": response.text,
                "status_code": response.status_code,
            }
        finally:
            return resp

    # Main method
    def get_predictions(self, home: str, away: str, net=True):
        """Get predictions for matches

        Args:
            home (str): Home team
            away (str): Away team
            net (bool, optional): Fetch data from internet. Defaults to True.

        Returns:
            _type_: _description_
        """
        data = {"home": home, "away": away, "net": net}
        resp = self.__requester(url=path.join(self.url, "predict"), json=data)
        if resp["succeed"] and resp["status_code"] == 200:
            prediction_response = (True, loads(resp["feedback"]))
        else:
            prediction_response = (False, resp["feedback"])
        return prediction_response

    def __call__(self, *args, **kwargs):
        return self.get_predictions(*args, **kwargs)


if __name__ == "__main__":
    matches = (
        ["Chelsea", "Arsenal"],
        ["Real Madrid", "Barcelona"],
        ["Inter Milan", "Juventus"],
        ["PSG", "Monaco"],
    )
    run = predictor(
        api_url="http://localhost:8000/v1",
        token="12345",
    )
    for match in matches:
        predictions = run.get_predictions(home=match[0], away=match[1], net=False)
        if predictions[0]:
            print(f'{"-".join(match)} : {predictions[1]}')
        else:
            print(f"Error : {predictions[1]}")
# Output
"""
Chelsea-Arsenal : {'choice': 71.43, 'g': 7.5, 'gg': 55.0, 'ov15': 55.0, 'ov25': 40.0, 'ov35': 20.0, 'pick': '2', 'result': '2'}
Real Madrid-Barcelona : {'choice': 62.5, 'g': 9.0, 'gg': 90.0, 'ov15': 60.0, 'ov25': 45.0, 'ov35': 30.0, 'pick': 'gg', 'result': '2'}
Inter Milan-Juventus : {'choice': 55.56, 'g': 7.0, 'gg': 70.0, 'ov15': 40.0, 'ov25': 25.0, 'ov35': 10.0, 'pick': 'gg', 'result': '1'}
PSG-Monaco : {'choice': 57.14, 'g': 13.0, 'gg': 80.0, 'ov15': 75.0, 'ov25': 55.0, 'ov35': 45.0, 'pick': 'gg', 'result': '2'}
"""
