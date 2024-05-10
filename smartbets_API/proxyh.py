# Hunts down open proxies from github
from random import choice
from pyfreeproxies import UpdateAwareFreeProxies


class hunter45:
    def __init__(self):
        self.picked = []
        self.freeProxies = UpdateAwareFreeProxies()

    def get_proxy(self) -> list:
        """fetches proxy"""
        try:
            return (True, self.freeProxies.get_confirmed_working_proxies())
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
                return pk

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
