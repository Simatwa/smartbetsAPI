# Hunts down open proxies from github
from random import choice


class hunter45:
    def __init__(self, requests: object):
        self.links = {
            "socks5": "https://github.com/TheSpeedX/PROXY-List/raw/master/socks5.txt",
            "socks4": "https://github.com/TheSpeedX/PROXY-List/raw/master/socks4.txt",
            "https": "https://github.com/TheSpeedX/PROXY-List/raw/master/http.txt",
        }
        self.requests = requests
        self.type = "socks5"
        self.picked = []

    def get_proxy(self, type: str = "socks5") -> list:
        """fetches proxy"""
        try:
            self.type = type
            rp = self.requests.get(self.links[type])
            if rp.status_code == 200:
                return (True, rp.text.split("\n"))
        except Exception as e:
            return (False, e.args[1] if len(e.args) > 1 else e)

    def sample(self, current_proxies: list = []) -> dict:
        if len(current_proxies) > 1:

            def pick():
                pk = choice(current_proxies)
                if pk in self.picked:
                    return pick()
                try:
                    current_proxies.remove(pk)
                except:
                    pass
                return self.type + "://" + pk

            pk = pick()
            return (
                True,
                {
                    "http": pk,
                    "https": pk,
                },
            )
        else:
            self.type = choice(list(self.links.keys()))
            sp = self.get_proxy()
            if sp[0]:
                return True, self.sample(sp[1])
            else:
                return sp


if __name__ == "__main__":
    import requests as req

    run = hunter45(req)
    all_proxies = run.get_proxy()[1]
    for x in all_proxies:
        print(run.sample(all_proxies))
