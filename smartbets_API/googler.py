from .bet_common import *
from .html_fetcher import web
import random as rand


class google_net:
    def __init__(self):
        self.one, self.stat, self.done, self.stat2 = [], "/url?q=", [], "/url?esrc"
        self.unwanted = ["women", "u1", "u20", "u21", "u2", "-ii"]

    # Determines integrity of the url
    def verify(self, url):
        ln = len(url)
        if url.endswith("/"):
            if url[ln - 4 : ln - 1].isdigit():
                resp = True
            else:
                resp = False
        elif url[ln - 3 : ln].isdigit():
            resp = True
        else:
            resp = False
        return resp

    # Generates random Google-query params
    def sampl(self):
        web = "soccerway.com"
        key = [
            f"matches in ke.{web}",
            f"in int.{web} website",
            f"in {web}",
            f"football club in ca.{web}",
            f"Performance in {web}",
            f"in {web}",
            f"matches in ke.{web}",
            f"Fixtures in {web}",
        ]
        return rand.choice(key)

    # Handling https link @start
    def httpSearch(self, url):
        if self.verify(url):
            return url
        else:
            return 0

    # Handling  non https links @start
    def statSearch(self, url):
        url1 = url.replace(self.stat, "")
        target = []
        link = ""
        for letter in url1:
            if letter == "&":
                break
            target.append(letter)
        for letter in target:
            link = link + letter
        if self.verify(link):
            return link
        else:
            return 0

    # Launching link-hunt
    def statSearch2(self, url):
        url = url.split("=")
        resp = 0
        for link in url:
            if link[0:5] == "https":
                amp = link.find("&")
                if amp > 0:
                    resp = link[0:amp]
        return resp

    def linkHunter(self):
        for url in self.one:
            if url[0:7] == self.stat:
                ans = self.statSearch(url)
            elif url[0:5] == "https":
                ans = self.httpSearch(url)
            elif url[0:9] == self.stat2:
                ans = self.statSearch2(url)
            if ans:
                self.done.append(ans)

    # Souping 'a' links from raw html
    def first(self, soup):
        links = soup.find_all("a")
        for entry in links:
            url = str(entry.get("href")).strip()
            if ".soccerway.com/teams" in url:
                self.one.append(url)
                for data in self.unwanted:
                    if data in url.lower():
                        try:
                            self.one.remove(url)
                        except:
                            pass

    # Main method
    def glinkFinder(self, team):
        if not "fc" in team.lower():
            team = team + " fc"
        link = google(f"{team} {self.sampl()}")
        soup = souper(web().fetcher(link, 0))
        self.first(soup)
        self.linkHunter()
        return self.done
