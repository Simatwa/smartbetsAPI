import os
import sqlite3
import subprocess
from sys import exit, prefix
import colorama as col


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


def createDir():
    from appdirs import AppDirs

    dirs = AppDirs("Smartwa", "smartbets_API")
    root = dirs.user_data_dir + "/"
    try:
        if not os.path.isdir(root):
            os.makedirs(root)
    except PermissionError:
        exit(col.Fore.RED + "[*] Run with Sudo PERMISSION!" + col.Fore.RESET)
    except Exception as e:
        pass
    dir = ["database", "log", "text", "analyzed"]
    for data in dir:
        if not os.path.isdir(root + data):
            try:
                os.mkdir(root + data)
            except Exception as e:
                print(f"ERROR : {root+data} - {e}")
    dbnm = root + "database/smartBet2.db"
    return dbnm, root


dbnm, root = createDir()
# Ensures script run with enough permissions
def confirm_sudo():
    try:
        with open(root + "pid", "w") as file:
            file.write(str(os.getpid()))
    except PermissionError:
        exit(col.Fore.RED + "[*] Run with Sudo PERMISSION!" + col.Fore.RESET)
    except Exception as e:
        pass


confirm_sudo()
# Handles db
class database:
    def __init__(self):
        pass

    # Interacts with dbs (sql commands)
    def queryDb(self, sql):
        conn = sqlite3.connect(dbnm)
        csr = conn.cursor()
        try:
            dat = csr.execute(sql)
            data = csr.fetchall()
        except Exception as e:
            data = "0"
        else:
            conn.commit()
            if not data:
                data = "0"
        finally:
            csr.close()
            conn.close()
        return data

    # Inserting data into db[2]
    def insertDb(self, table, col1, col2, data1, data2):
        conn = sqlite3.connect(dbnm)
        csr = conn.cursor()
        run = f"INSERT INTO {table}({col1},{col2}) VALUES(?,?)"
        try:
            csr.execute(run, (data1, data2))
            csr.close()
        except:
            pass
        conn.commit()
        conn.close()
        # Inserting data into db[1]

    def insertDb2(self, table, col, data):
        conn = sqlite3.connect(dbnm)
        csr = conn.cursor()
        run = f"INSERT INTO {table}({col}) VALUES(?)"
        try:
            csr.execute(run, (data))
            csr.close()
        except:
            pass
        conn.commit()
        conn.close()
        # Updating db data

    def updateDb(self, id, column, data, table):
        if type(id) is str:
            id = ["Id", id]
        try:
            conn = sqlite3.connect(dbnm)
            csr = conn.cursor()
            run = (
                f"""UPDATE  {table} SET  {column}='{data}'  WHERE {id[0]}='{id[1]}' """
            )
            csr.execute(run)
            csr.close()
            conn.commit()
            conn.close()
        except Exception as e:
            pass


class set_config:
    def __init__(self, args):
        self.args = args
        self.target = ["log", "color", "filename", "gui", "level"]
        self.db = database()

    # Creates db initially
    def createTable(self):
        self.db.queryDb("DROP TABLE Booter")
        run = f"""CREATE TABLE IF NOT EXISTS Booter(ID INTEGER PRIMARY 
		KEY AUTOINCREMENT, log TEXT, Color TEXT, Filename TEXT, Gui TEXT, Level INTEGER)"""
        self.db.queryDb(run)

    def main(self):
        self.createTable()
        log = self.args.log if self.args.log else False
        color = self.args.color if self.args.color else False
        filename = self.args.filename if self.args.filename else False
        gui = self.args.gui if self.args.gui else False
        level = self.args.level
        self.db.queryDb(
            f"""INSERT INTO Booter(log,color,filename,gui,level)
		VALUES('{log}','{color}','{filename}','{gui}','{level}')"""
        )
