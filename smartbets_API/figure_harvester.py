from .html_fetcher import web
from .bet_common import *
from .googler import google_net


class harvest:
    def __init__(self):
        self.score, self.win, self.draw, self.loss, self.usedName = {}, [], [], [], []

    # Overall performance
    def queryTeams(self, tbl):
        tms = convToList(queryDb(f"SELECT Name FROM {tbl}"))
        return tms

    def getTeamsB(self, tbl, soup=False):
        logging.debug("Updating Teams B")
        one = soup.find_all("div", {"class": "submenu_dropdown"})
        soup1 = souper(one)
        t1 = soup1.find_all("option")
        availableT = self.queryTeams(tbl)
        for line in t1:
            link = line.get("value")
            title = nameFinder(line)
            if link and title and not title in availableT:
                insertDb(f"{tbl}", "Name", "Url", title, link)

    # Getting Home  teams
    def getTeamsA(self, tbl="Team", soup=False):
        logging.debug("Updating Teams A")
        one = soup.find_all("td", {"class": "text team large-link"})
        soup1 = souper(one)
        t1 = soup1.find_all("a")
        availableT = self.queryTeams(tbl)
        for line in t1:
            link = line.get("href")
            title = line.get("title")
            if link and title and not title in availableT:
                insertDb(f"{tbl}", "Name", "Url", title, link)
        self.getTeamsB(tbl, soup=soup)

    # Classifying scores
    def performance(self, soup):
        logging.debug("Team Performance")
        targets = ["win", "draw", "loss"]
        x = 0
        for target in targets:
            a = soup.find_all("a", {"class": f"result-{target}"}, limit=1000)
            self.score[target] = len(a)
            x += 1
            for entry in a:
                result = nameFinder(entry)
                if x == 1:
                    self.win.append(result)
                elif x == 2:
                    self.draw.append(result)
                else:
                    self.loss.append(result)

    # Getting team position
    def position(self, st=0, st1=False, soup=False):
        keys = ["odd", "even"]
        a = soup.find_all("tr", {"class": f"{keys[st]} highlight team_rank"})
        if a:
            b = soupHtml(a[0], sp="\n")
            c = b.split("\n")
            logging.debug(f"Pos-Team-MP-D-P:\n{c}")
            return c[0]
        if st1:
            return str(0)
        else:
            return self.position(1, 2, soup)

    # Establishing dbs
    def createDb(self, tbl="Team"):
        logging.debug("Database Configuration")
        run = f"""CREATE TABLE IF NOT EXISTS {tbl}(
		Id INTEGER PRIMARY KEY AUTOINCREMENT,
		Name TEXT UNIQUE, Url TEXT UNIQUE, Creation_time TEXT)"""
        queryDb(run)

    # Main function
    def lenTeams(self):
        run = "SELECT COUNT(name) FROM league5"
        no = queryDb(run)
        return int(no[0][0])

    # Error detected ***
    def firstTeams(self, net=False):
        logging.warning("Updating league [5]")
        gui.toast("Updating League[5]")
        self.createDb("League5")
        self.createDb()
        top = [
            "int.soccerway.com/teams/england/manchester-city-football-club/676/",
            "int.soccerway.com/teams/spain/club-atletico-de-madrid/2020/",
            "int.soccerway.com/teams/germany/fc-bayern-munchen/961/",
            "int.soccerway.com/teams/italy/fc-internazionale-milano/1244/",
            "int.soccerway.com/teams/france/paris-saint-germain-fc/886/",
        ]
        for link in top:
            befNo = self.lenTeams()
            aftNo = 0
            soup = souper(web().fetcher(link, net))
            logging.info(nameFinder(soup.title))
            while aftNo <= befNo + 14:
                self.getTeamsA("league5")
                self.getTeamsA(soup=soup)
                aftNo = self.lenTeams()
            del soup

    # Verifies link's integrity
    def linkVerify(self, link):
        link2 = link
        x = 0
        while 1:
            if link[(len(link) - 2)].isdigit():
                return link
            elif x > 50 or len(link) < 4:
                return link2
            ind = link.rfind("/")
            link = link[0:ind]
            x += 1

    def harvester(self, name, net=True, linkF=False):
        self.createDb()
        # Handles teams that can't be found on Google
        if len(self.usedName) > 4 and self.usedName[0] == self.usedName[3]:
            axy = ({"win": 0, "draw": 0, "loss": 0}, [], [], [], 0)
            logging.warning(f"No data found for '{name}' ")
            data = f"{timeStamp} : '{name}' Team-info wasn't found on Web!"
            saver(data, link=f"{tbe}_report", fmt="txt", mode="a", dir="text/")
            self.usedName.clear()
            return axy
        if linkF:
            links = convToList(
                queryDb(f"SELECT url FROM Team WHERE url LIKE '%{linkF}' ")
            )
        else:
            links = convToList(
                queryDb(f"SELECT url FROM Team WHERE Name LIKE'%{name}' ")
            )
        if not "0" in links:
            x = 0
            link = links[0]
            if len(link) > 10:
                link = self.linkVerify(link)
                main = "https://ke.soccerway.com"
                if not "https" in link:
                    link = main + link
                soup = souper(web().fetcher(link, net))
                x += 1
                ct = nameFinder(soup.title).split("-")[:2]
                if len(ct) > 1:
                    logging.info(f"{ct[0]} - {ct[1]}")
                self.createDb()
                self.getTeamsA(soup=soup)
                self.performance(soup)
                if len(self.score) == 3:
                    pos = self.position(soup=soup)
                    if not pos.isdigit():
                        pos = 0
                    del soup, links
                    self.usedName.clear()
                    fdb = (self.score, self.win, self.draw, self.loss, int(pos))
                    return fdb
                else:
                    logging.warning(f"{x}.Link :'{link}' failed!")
                    return self.harvester(name, net=True)
        else:
            logging.debug(f"{name} NOT in dbs")
            link = google_net().glinkFinder(name)
            if link:
                logging.debug(f"{name} being Updated")
                insertDb("Team", "Name", "Url", name, link[0])
                return self.harvester(name, net=net, linkF=link[0])
            else:
                logging.debug("Zero G-links Found")
        self.usedName.append(name)
        return self.harvester(name, net=True)
