# win,draw,loss evaluater
from .bet_common import getInt, tScore, logging

# Getting performance generally
def GG(results):
    g = gg = ov15 = ov25 = ov35 = df = 0
    dwn = str(results).count("-")
    if dwn:
        df = 100 / dwn
    else:
        df += 0.0000001
        logging.debug("Empty list in tertiary_bet")
        return [g, gg, ov15, ov25, ov35]
    for x in range(3):
        for score in results[x]:
            res = getInt(score)
            sm = sum(res)
            if max(res) and min(res):
                gg += df
            if sm >= 2:
                ov15 += df
            if sm >= 3:
                ov25 += df
            if sm >= 4:
                ov35 += df
            if not x == 2:
                g += max(res)
            else:
                if min(res):
                    g += min(res)
    return [g, gg, ov15, ov25, ov35]


# Getting performance per team level
def GG1(results):
    g = gg = ov15 = ov25 = ov35 = df = 0
    dwn = str(results).count("-")
    if dwn:
        df = 100 / dwn
    else:
        df += 0.000001
        return [g, gg, ov15, ov25, ov35]
    for x in range(3):
        for score in results[x]:
            res = getInt(score)
            if not x == 2:
                sm = max(res)
                g += sm
                if sm:
                    gg += df
                    if sm >= 2:
                        ov15 += df
                    if sm >= 3:
                        ov25 += df
                    if sm >= 4:
                        ov35 += df
            else:
                sm = min(res)
                if sm:
                    g += sm
                    gg += df
                    if sm >= 2:
                        ov15 += df
                    if sm >= 3:
                        ov25 += df
                    if sm >= 4:
                        ov35 += df
    return [g, gg, ov15, ov25, ov35]


def tertiary(wdl):
    No = str(wdl).count("-")
    logging.debug(f"WDL Received [{No}].\n{wdl}")
    G1 = GG(wdl)
    G2 = GG1(wdl)
    t = ["g", "gg", "ov15", "ov25", "ov35"]
    for x in range(1, 5):
        t[x] = round((G1[x] + G2[x]) / 2, 2)
    del wdl
    return [G1[0], t[1], t[2], t[3], t[4]]
