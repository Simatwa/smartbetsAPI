import datetime, sqlite3, os, time, re, traceback, sys, calendar, subprocess
from bs4 import BeautifulSoup as bts
from .configuration_handler import dbnm, root
from random import randint
import logging as log
import colorama as col
import threading as thr
import colorama as col

version = 1.1
config = {}
env = {"api": False}
now, ht = datetime.datetime.today(), "text/"
timeNow = now.strftime("%H:%M:%S")
timeStamp = now.strftime("%d_%b_%Y-%H_%M_%S.")
tablee = now.strftime("%b_%d_%Y")
tbe = "Bet_" + tablee
predictionTb = "Prediction_" + tablee
developer = "Smartwa"
root_image = os.getcwd() + "static/image/"
logo = root_image + "logo.jpg"
predbets_img = root_image + "predbets.png"
# Runs system cmds at API level
def get_output(command):
    success = False
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        success = True
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        # check_call can raise other exceptions, such as FileNotFoundError
        output = str(e)
    return (success, output)


# Gets environment [tar termux]
def environ_setup():
    if "termux" in str(sys.prefix).lower():
        env["api"] = True
        """
		if 'version' and 'maintainer'  in str(get_output('pkg show termux-api')[1]).lower():
			env['api']=True
		else:
			if not 'pydroid' in str(sys.prefix).lower():
				opt=input('Install Termux-API.  [Y/n]:')
				if opt.lower()=='y':
					os.system('pkg install termux-api')
					print('Termux-api will function on next run!')
		"""


environ_setup()


def filter_str(fnm, sp="_"):
    un = [t for t in str(fnm) if not t.isalnum() and not t in list(sp)]
    for val in un:
        fnm = str(fnm).replace(val, "")
    return str(fnm)


# Gets latest time
def c_time():
    now = datetime.datetime.today()
    rp = now.strftime("%d-%b-%Y %H:%M:%S")
    return rp


def correctDt(no):
    if not str(no)[0] == "0" and int(no) < 10:
        no = "0" + str(no)
    return no


def cent():
    tm = sys.prefix
    if "termux" in tm:
        return 45
    else:
        return 37


def tableDay(day="none", month=False, yr=now.year):
    if str(day).isdigit() and not month:
        no = correctDt(day)
        no = now.strftime(f"%b_{no}_{yr}")
    elif str(day).isdigit() and str(month).isdigit():
        no = correctDt(day)
        no = now.strftime(f"{calendar.month_abbr[int(month)]}_{no}_{yr}")
    else:
        no = tablee
    return no


def showProgress(value, total, msg="Processing"):
    dev = 0
    pre = sys.prefix
    tm = 13
    if "termux" in str(pre):
        tm = 20
    resp = f"•{msg}-{'#'*tm}~[{round(((value*100)/total)+dev,2)} %] "
    return resp


# Converts datatype to list
def convToList(data):
    file8 = []
    for dat in data:
        file8 = file8 + list(dat)
    return file8


# Filters out non-alnum x-ters from string
def filter(link, fmt=""):
    link = str(link)
    for data in link:
        if not data.isalnum() and data != "_":
            link = link.replace(data, "")
    return link + "." + fmt


# Running sql statements against db
def queryDb(sql):
    conn = sqlite3.connect(dbnm)
    csr = conn.cursor()
    try:
        dat = csr.execute(sql)
        data = csr.fetchall()
    except:
        data = "0"
    else:
        conn.commit()
        if not data:
            data = "0"
    finally:
        csr.close()
        conn.close()
    return data


def sample4(a=10000, b=99999):
    return " " + str(randint(a, b))


# Inserting data into db[2]
def insertDb(table, col1, col2, data1, data2):
    tm4 = c_time() + sample4()
    conn = sqlite3.connect(dbnm)
    csr = conn.cursor()
    run = f"INSERT INTO {table}({col1},{col2},Creation_time) VALUES(?,?,?)"
    try:
        csr.execute(run, (data1, data2, tm4))
        csr.close()
        conn.commit()
        conn.close()
    except:
        pass
    return tm4


# Inserting data into db[1]
def insertDb2(table, col, data):
    conn = sqlite3.connect(dbnm)
    csr = conn.cursor()
    run = f"INSERT INTO {table}({col}) VALUES(?)"
    try:
        csr.execute(run, (data))
        csr.close()
        conn.commit()
        conn.close()
    except:
        pass


# Updating db data
def updateDb(id, column, data, table):
    if type(id) is str:
        id = ["Id", id]
    try:
        conn = sqlite3.connect(dbnm)
        csr = conn.cursor()
        run = f"""UPDATE  {table} SET  {column}='{data}'  WHERE {id[0]}='{id[1]}' """
        csr.execute(run)
        csr.close()
        conn.commit()
        conn.close()
    except:
        pass


# Soups data
def souper(html, prett=False):
    nm = bts(str(html), "html.parser")
    if prett:
        nm = nm.prettify()
    return nm


# Filters out irrelevant tags
def soupHtml(data, amt=2, sp="", pret=0):
    soup = souper(data)
    if int(amt) == 1:
        lst = ["script"]
    else:
        lst = ["script", "style"]
    for data in soup(lst):
        data.decompose
    after = f"{sp}".join(soup.stripped_strings)
    if pret:
        soup = souper(after)
        after = soup.prettify()
    return str(after)


# Getting names from Html
def nameFinder(html, sp=""):
    name = soupHtml(html, 2, sp)
    name = name.replace("'", "")
    if str(name).lower() == "none":
        name = "?"
    return name


# Generating google search link
def google(search):
    key = re.sub("\s", "+", search)
    stat = f"""https://www.google.com/search?q={key}"""
    return stat


# Saves text-like files
def saver(data, link, fmt, mode="w", dir=ht):
    fnm = filter(link, fmt)
    data = souper(data, 1)
    with open(root + dir + fnm, mode) as file:
        file.write(data)
        file.close()


# Opens file (txt,html)
def opener(link, fmt="html"):
    try:
        with open(ht + filter(link, fmt)) as file:
            data = file.read()
    except:
        data = 0
    finally:
        return data


def getInt(score):
    score = re.sub("\s", "", score)
    after = []
    score = score.split("-")
    for dat in score:
        for letter in dat:
            if not letter.isdigit():
                dat = dat.replace(letter, "")
        after.append(int(dat))
    return after


# Analysing results
def tScore(score):
    sA, sB = [], []
    for fig in score:
        if not fig:
            fig = "0-0"
        integ = getInt(fig)
        sA.append(min(integ))
        sB.append(max(integ))
    return [sum(sA), sum(sB)]


# Handles the config passed
def run(cmd):
    osr = lambda a: os.system(a)
    try:
        t = thr.Thread(
            target=osr,
            args=(cmd,),
        )
        t.start()
        t.join(timeout=1)
    except:
        pass


# Updates configurations parsed
class booter:
    def __init__(self):
        self.target = ["log", "color", "filename", "gui", "level"]

    def get_info(self):
        info = queryDb(f'SELECT {",".join(self.target)} FROM Booter WHERE ID=1')[0]
        for x in range(len(self.target)):
            if str(info[x]).lower() in ("false", "0", "none"):
                config[self.target[x]] = False
            else:
                config[self.target[x]] = info[x]


booter().get_info()
# Logging configurations
def log_level():
    tg = int(config["level"])
    return tg if tg > 0 else 60


if config.get("log"):
    fnm = config.get("filename")
    if fnm:
        fnm = filter_str(fnm, "._")
        if not "." in fnm:
            fnm = fnm + ".log"
        if "/" in fnm:
            try:
                os.makedirs(os.path.split(fnm[0]))
            except:
                pass
        else:
            fnm = "/log/" + fnm
    else:
        fnm = "/log/" + timeStamp + "log"
    log.basicConfig(
        format="%(asctime)s - %(levelname)s : %(message)s",
        datefmt="%H:%M:%S",
        level=log_level(),
        filename=root + fnm,
    )
else:
    log.basicConfig(
        format="%(asctime)s - %(levelname)s : %(message)s",
        datefmt="%H:%M:%S",
        level=log_level(),
    )
# COLOR CONFIG
bold = col.Style.NORMAL
if config.get("color"):

    class logging:
        def __init__(self):
            self.color = self.color()

        class color:
            grey = "\x1b[38;20m"
            yellow = "\x1b[33;20m"
            red = "\x1b[31;20m"
            bold_red = "\x1b[31;1m"
            reset = "\x1b[0m"
            reset = col.Fore.GREEN

        def debug(self, arg):
            log.debug(bold + self.color.grey + arg + self.color.reset)

        def info(self, arg):
            log.info(bold + col.Fore.CYAN + arg + self.color.reset)

        def warning(self, arg):
            log.warning(bold + self.color.yellow + arg + self.color.reset)

        def error(self, arg):
            log.error(bold + self.color.red + arg + self.color.reset)

        def critical(self, arg):
            log.critical(bold + self.color.bold_red + arg + self.color.reset)

else:

    class logging:
        def __init__(self):
            self.color = self.color()

        class color:
            reset = ""  # col.Fore.GREEN

        def debug(self, arg):
            log.debug(arg + self.color.reset)

        def info(self, arg):
            log.info(arg + self.color.reset)

        def warning(self, arg):
            log.warning(arg + self.color.reset)

        def error(self, arg):
            log.error(arg + self.color.reset)

        def critical(self, arg):
            log.critical(arg + self.color.reset)


logging = logging()
if env["api"] and config.get("gui"):

    class guint:
        def __init__(sel):
            pass

        def toast(self, msg, s="-s", g="bottom", b="darkgray", c="lime"):
            if not s:
                s = ""
            run(f"termux-toast -g {g} -b {b} -c {c} {s} {msg}")

        def notify(self, msg, t="Smartbets", gr=1, id=1, img=logo):
            run(
                f"termux-notification -t {t} -c {'-'.join(msg.split(' '))} --group {gr} --id {id} --image-path {img}"
            )

        def remove(self, id=1110):
            run(f"termux-notification-remove {id}")

        def vibrate(self, d=1, f=""):
            if bool(f):
                f = "-f"
            run(f"termux-vibrate -d {str(d*150)} {f}")

        def speak(
            self,
            msg,
            r=1.0,
            p=1.0,
            s="MUSIC",
        ):
            run(f"termux-tts-speak -p {p} -r {r} -s {s} {msg}")

else:

    class guint:
        def __init__(self):
            pass

        def toast(self, msg, s="-s", g="top", b="gray", c="lime"):
            pass

        def notify(self, msg, t="Smartbets", gr=1, id=1110, img=False):
            pass

        def remove(self, id=1110):
            pass

        def vibrate(self, d=1, f=False):
            pass

        def speak(self, msg, p=1.0, r=1.0, s="MUSIC"):
            pass


# terminates the program
def exit_t(msg=""):
    logging.critical(f"Healthy exit ~ {msg}")
    sys.exit(
        col.Fore.YELLOW
        + f"[*] Goodbye! ^Regards:{col.Fore.GREEN+developer}"
        + col.Fore.RESET
    )


gui = guint()
gui.toast("SmartbetsAPI running", b="red", s=False, c="yellow", g="top")
gui.speak(f"Regards : {developer}")
gui.notify(f"{developer.split(' ')[0]}", "Developer", 1.0, 1.0, logo)
