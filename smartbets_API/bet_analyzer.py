from .bet_common import logging, getInt, tScore
from .tertiary_bet import tertiary
import os
import re


class analyze:
    def __init__(self):
        self.gSco, self.gCon = [], []

    # Converts  goal-scored  to  (%)
    def goaler(self, amt, total):
        try:
            perc = (amt * 100) / total
        except:
            return 0
        return perc

    # Determines total scores (%)
    def nScores(self, amt, over=5):
        perc = (amt * 100) / over
        return perc

    # Determines team position (%)
    def positioner(self, pos, amt=20):
        one = 100 / amt
        before = pos * one
        if before == 0:
            return 0
        return (100 + one) - before

    # Main function (Fig analysis controller)
    def analyzer(self, coded):
        logging.debug(f"Analyzing {len(coded)} item(s)")
        scores = coded[0]
        position = coded[4]
        t = ["score", "win", "draw", "loss", "position"]
        n = ["nWin", "nDraw", "nLoss"]
        for x in range(3):
            n[x] = scores[t[x + 1]]
        for x in range(3):
            t[x + 1] = coded[x + 1]
        wdl = [t[1], t[2], t[3]]
        _pos = self.positioner(position)
        _nWin = self.nScores(n[0])
        _nDraw = self.nScores(n[1])
        _nLoss = self.nScores(n[2])
        # updating goals
        for x in range(1, 4):
            analyzed = tScore(t[x])
            if x == 1 or x == 2:
                self.gSco.append(max(analyzed))
                self.gCon.append(min(analyzed))
            if x == 3:
                self.gSco.append(min(analyzed))
                self.gCon.append(max(analyzed))
        y = sum(self.gSco)
        z = sum(self.gCon)
        gTotal = y + z
        _gSco = self.goaler(y, gTotal)
        _gCon = self.goaler(z, gTotal)
        analysis = {
            "position": _pos,
            "win": _nWin,
            "draw": _nDraw,
            "loss": _nLoss,
            "scored": _gSco,
            "conceived": _gCon,
        }
        tertia = tertiary(wdl)
        return (analysis, tertia)
