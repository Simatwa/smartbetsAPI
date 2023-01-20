class args_handler:
    def __init__(self, **kwargs):
        v = lambda t: kwargs[t]
        self.log = v("log")
        self.color = v("color")
        self.filename = v("filename")
        self.gui = v("gui")
        self.level = v("level")


class predictor:
    def __init__(
        self,
        include_position=False,
        log=False,
        level=0,
        filename=None,
        color=False,
        gui=False,
        api=False,
    ):
        if not api:
            from .configuration_handler import set_config

            args = {
                "log": log,
                "color": color,
                "filename": filename,
                "gui": gui,
                "level": level,
            }
            set_config(args_handler(**args)).main()
        from .bet_common import logging
        from .bet_analyzer import analyze
        from .figure_harvester import harvest

        self.logging, self.harvest, self.analyze = logging, harvest, analyze
        (
            self.position,
            self.res,
            self.A,
            self.B,
            self.aA,
            self.bB,
            self.Af,
            self.Bf,
            self.nF,
        ) = (include_position, "result", [], [], [], [], [], [], {})
        self.zero = {
            "g": 0.0,
            "gg": 0.0,
            "ov15": 0.0,
            "ov25": 0.0,
            "ov35": 0.0,
            "choice": 0.0,
            "result": "0",
            "pick": "0",
        }
        self.recv = (
            {
                "position": 0,
                "win": 0.0,
                "draw": 0.0,
                "loss": 0.0,
                "scored": 0,
                "conceived": 0,
            },
            [0, 0.0, 0.0, 0.0, 0.0],
        )

    # Updates team data in corresponding list
    def update(self, data, opt):
        if opt == 1:
            self.A.clear()
            for val in data:
                self.A.append(val)
        else:
            self.B.clear()
            for val in data:
                self.B.append(val)

    # Exlusively unpacks team-data
    def decide4(self, data, lst):
        pos = ["position", "win", "draw", "loss", "scored", "conceived"]
        for x in range(6):
            pos[x] = data[pos[x]]
        scored, conceived = pos[4], pos[5]
        classA = ((pos[1] + pos[2] + (100 - pos[3])) / 300) * 100
        classB = ((pos[4] + (100 - pos[5])) / 200) * 100
        final = [pos[0], classA, classB]
        self.update(final, lst)

    # Handling results
    def resulter(self):
        two = [self.A[1], self.B[1]]
        self.aA.clear()
        self.bB.clear()
        if max(two) - min(two) <= 10:
            # Adding  goals  in performance deter
            a, b = (sum([self.A[1], self.A[2]]) / 200) * 100, (
                sum([self.B[1], self.B[2]]) / 200
            ) * 100
            self.aA.insert(0, a)
            self.bB.insert(0, b)
        else:
            self.aA.insert(0, self.A[1])
            self.bB.insert(0, self.B[1])
        # Using position in determining result
        if self.position and self.A[0] and self.B[0]:
            self.logging.info(
                f"% of Positions {round(self.A[0],2)}-{round(self.B[0],2)}"
            )
            self.logging.info(f"% Before {round(self.aA[0],2)}-{round(self.bB[0],2)}")
            y = ((self.aA[0] + self.A[0]) / 200) * 100
            z = ((self.bB[0] + self.B[0]) / 200) * 100
            self.aA.insert(0, y)
            self.bB.insert(0, z)
            self.logging.info(f"% After {round(self.aA[0],2)}-{round(self.bB[0],2)}")

    # Equates the two percentages into one
    def evaluater_(self, percs: list) -> list:
        perc_f = lambda v: (v * 100) / sum(percs)
        return [perc_f(percs[0]), perc_f(percs[1])]

    # AI function
    def finalizer(self):
        y, z = self.aA[0], self.bB[0]
        aft = self.evaluater_([y, z])
        if max(aft) - min(aft) <= 10:
            if max(aft) - min(aft) <= 1:
                self.nF[self.res] = "X"
            else:
                if max(aft) == y:
                    self.nF[self.res] = "1X"
                else:
                    self.nF[self.res] = "X2"
        else:
            if y > z:
                self.nF[self.res] = "1"
            else:
                self.nF[self.res] = "2"
        return aft

    # Displays received teams
    def display(self, data, aft):
        if type(data) is list:
            try:
                self.logging.info(data[0].capitalize() + " vs " + data[1].capitalize())
            except:
                pass
        else:
            self.logging.info(data[1].capitalize() + " vs " + data[2].capitalize())
        self.logging.info(f"{round(aft[0],2)} {'*'*5} {round(aft[1],2)}")

    # Computing tertiary predictions (over,GG)
    def analyFn(self, data=0, opt=0):
        finale, all = {}, ["g", "gg", "ov15", "ov25", "ov35"]
        if opt == 1:
            self.Af.extend(data)
        elif opt == 2:
            self.Bf.extend(data)
        else:
            finale.clear()
            for x in range(5):
                finale[all[x]] = (self.Af[x] + self.Bf[x]) / 2
            return finale

    # Determines the final FINAL bet
    def pick(self, dic):
        bef = []
        key = list(dic.keys())
        ch = "__"
        bef.clear()
        t = ["g", "gg", "ov15", "ov25", "ov35", "choice", "result"]
        for x in range(7):
            t[x] = dic[t[x]]
        for x in range(7):
            if x == 6:
                continue
            bef.append(t[x])
            fnl = max(bef)
        for x in range(7):
            if t[x] == fnl:
                ch = key[x]
            if ch == "choice":
                ch = dic["result"]
        return ch

    # Combines the final decision and other predictions
    def render(self, teams):
        self.resulter()
        aft = self.finalizer()
        self.display(teams, aft)
        predi = self.analyFn()
        result = self.nF[self.res]
        scr = [self.aA[0], self.bB[0]]
        rslt = round((max(scr) * 100) / sum(scr), 2)
        predi["choice"] = rslt
        predi[self.res] = result
        predi["pick"] = self.pick(predi)
        return predi

    # Clear global variable's data
    def clearHolders(self):
        self.A.clear
        self.B.clear()
        self.aA.clear()
        self.bB.clear()
        self.Af.clear()
        self.Bf.clear()
        self.nF.clear()
        try:
            del aft
        except:
            pass

    # Handles list data-type
    def predictorL(self, teams: list, net=True) -> dict:
        self.clearHolders()
        for x in range(2):
            mined = self.harvest().harvester(teams[x], net)
            analysis = self.analyze().analyzer(mined)
            if analysis == self.recv:
                return self.zero
            self.decide4(analysis[0], x + 1)
            self.analyFn(analysis[1], x + 1)
        return self.render(teams)

    # Handles dict data-type
    def predictorD(self, teams: dict, net=True) -> dict:
        self.clearHolders()
        for key, value in teams.items():
            mined = self.harvest().harvester(value, net)
            analysis = self.analyze().analyzer(mined)
            if analysis == self.recv:
                return self.zero
            self.decide4(analysis[0], key)
            self.analyFn(analysis[1], key)
        return self.render(teams)
