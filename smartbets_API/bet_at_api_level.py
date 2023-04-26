from requests import Session
from json import loads
from sys import exit
from os import path


class predictor:
    def __init__(self, api_url: str, password: str, username="API"):
        """Connect to the REST API

        Args:
            api_url (str): Link to API
            password (str): API's password
            username (str, optional): API's username. Defaults to "API".
        """
        self.url = api_url
        self.username = username
        self.password = password
        self.session = Session()
        # Verifies the login credentials
        __login_trial = self.__api_login()
        if not __login_trial["status_code"] == 200:
            exit(__login_trial["feedback"])

    # Tries to login
    def __api_login(self):
        data = {"user": self.username, "paswd": self.password}
        login_trial = self.__requester(
            url=path.join(self.url, "login"), param=data, method="post"
        )
        return login_trial

    # Interacts with the api
    def __requester(self, url, param=False, method="get"):
        query_parameters = {"url": url}
        if param:
            query_parameters["params" if method == "get" else "data"] = param
        try:
            if method.lower() == "post":
                response = self.session.post(**query_parameters)
            else:
                response = self.session.get(**query_parameters)
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
    def get_predictions(self, home: str, away: str, net=True) -> list:
        """Get predictions for matches 

        Args:
            home (str): Home team 
            away (str): Away team
            net (bool, optional): Fetch data from internet. Defaults to True.

        Returns:
            list: list containing success report (bool) and predictions (dict)
        """
        data = {"home": home, "away": away, "net": net}
        resp = self.__requester(url=path.join(self.url,'predict'), param=data)
        if resp["succeed"] and resp["status_code"] == 200:
            prediction_response = (True, loads(resp["feedback"]))
        else:
            prediction_response = (False, resp["feedback"])
        return prediction_response

    def __call__(self,*args,**kwargs):
        return self.get_predictions(*args,**kwargs)


if __name__ == "__main__":
    matches = (
        ["Chelsea", "Arsenal"],
        ["Real Madrid", "Barcelona"],
        ["Inter Milan", "Juventus"],
        ["PSG", "Monaco"],
    )
    run = predictor(
        api_url="http://localhost:8000",
        password="mypass9876",
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
