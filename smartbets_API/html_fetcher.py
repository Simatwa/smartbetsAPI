from .bet_common import *
import requests as req
import random as rand
from faker import Faker


class web:
    def __init__(self):
        self.used, self.exc, self.user_agent, self.ref = [], [], [], []

    def sampl(self):
        etc = [
            "int",
            "ke",
            "us",
            "ca",
            "uk",
            "ca",
            "id",
            "cn",
            "de",
            "au",
            "gh",
            "in",
            "ie",
            "my",
            "ng",
            "nr",
            "sg",
            "za",
            "es",
            "el",
            "fr",
            "gr",
            "it",
            "kr",
            "nl",
            "pl",
            "pt",
            "br",
            "ro",
            "th",
            "tr",
            "ru",
            "ar",
        ]
        add = rand.choice(etc)
        if len(self.used) == len(etc):
            return add
        elif add in self.used:
            return self.sampl()
        else:
            if not add in self.used:
                self.used.append(add)
            return add

    def repair(self, url):
        if "soccerway.com/teams/" in url:
            stro = url.find(".")
            ln = len(url)
            return self.sampl() + url[stro:ln]
        return url

    # Counter-checks http status_code
    def status(self, code, reason):
        inf = f"{code} : {reason}"
        if not code == 200:
            logging.warning(f"{code} - {reason}")
        else:
            logging.debug(inf)

    # Generating request headers
    def header(self, user_ag=False):
        if not user_ag:
            user_ag = self.user_agent
        google = "https://www.google.com/"
        if user_ag:
            userA = self.user_agent[0]
            referer = google
            if self.ref:
                referer = self.ref[0]
            setchF = "same-origin"
        else:
            userA = f"{Faker().user_agent()}"
            referer = google
            setchF = "none"
            self.user_agent.insert(0, userA)
        content = {
            "Accept": "text/html, application/xhtml+xml, application/xml",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": referer,
            "X-Requested-With": "com.opera.mini.native.beta",
            "Connection": "Keep-Alive",
            "User-Agent": userA,
            "Sec-Fetch-Site": setchF,
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        }
        return content

    # Getting html from web
    def sender(self, link, info="Requesting", g=0, head=0):
        ht = "http"
        if ht in link:
            url = link
        else:
            url = "https://" + link
        try:
            logging.info(f"{info} - {url}")
            resp = req.get(url=url, headers=self.header())
        except Exception as e:
            if len(self.exc) > 1:
                return "0"
            logging.error(str(e))
            self.exc.append("1")
            return self.sender(url, "Retrying")
        else:
            self.ref.insert(0, url)
            self.status(resp.status_code, resp.reason)
            try:
                content = resp.text
            except:
                pass
            finally:
                code = resp.status_code
                g += 1
                if not code == 200:
                    self.user_agent.clear()
                    gui.toast(f"Http-code {code}", b="red", c="lime")
                    logging.debug(f"{g}s of SLEEP")
                    time.sleep(g)
                    return self.sender(self.repair(url), "Retrying", g, 1)
                if "access denied" in soupHtml(content).lower():
                    logging.warning("ACCESS DENIED".center(37))
                    self.user_agent.clear()
                    logging.warning(f"{g}s of SLEEP")
                    time.sleep(g)
                    return self.sender(self.repair(url), "Retrying", g, 1)
                nm = filter(link, "html")
                queryDb(f"DELETE FROM html where F_name='{nm}' ")
                insertDb("Html", "F_name", "File", nm, content)
                return self.launcher(link)

    # Query link's contents from db
    def launcher(self, link):
        nm = filter(link, "html")
        stat = convToList(queryDb(f"SELECT file FROM html WHERE F_name='{nm}' "))[0]
        if len(stat) > 50:
            return stat
        else:
            return self.sender(link)

    # Initially creating db
    def createDb(self):
        run = """CREATE TABLE IF NOT EXISTS html(Id INTEGER PRIMARY KEY
			AUTOINCREMENT, F_name TEXT, File TEXT, Creation_time TEXT)"""
        queryDb(run)

    def amendDt(self, dte):
        dt = str(dte).split("-")
        if not correctDt(dt[2]) == dt[2]:
            dt.insert(2, "0" + dt[2])
        return dt[0] + "-" + dt[1] + "-" + dt[2]

    # Main method
    def fetcher(self, link=False, net=True):
        if not link:
            link = "livescore.mobi/football/" + str(self.amendDt(now.date())) + "/?tz=3"
        logging.debug(f"Web-requester Activated : {link}")
        self.createDb()
        if net == True:
            resend = self.sender(link)
        else:
            resend = self.launcher(link)
        return resend
