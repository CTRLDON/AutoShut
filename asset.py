import json
from os import path , makedirs , path
from pynotifier import Notification
from plyer import notification
import logging
import datetime


def create_json():
    dirname = path.dirname(path.abspath(__file__))
    st = {
        "autostart": False,
        "error file": False,
    }

    st_json = json.dumps(st,indent=4)
    with open(path.join(dirname,"config.json"), "w") as file:
        file.write(st_json)


def create_logging_folder():
    folder = path.expanduser("~")
    logFolder = path.join(folder , "AppData/Local/GoTo/GoToShutdown")
    logFolder_exist = path.exists(logFolder)
    if logFolder_exist == False:
        makedirs(logFolder)
    logFile = path.join(folder , "AppData/Local/GoTo/GoToShutdown/error.txt")
    file_exist = path.exists(logFile)
    if file_exist == False:
        with open(logFile, 'w') as f: 
            f.write('This is an error file.')
    


def log(error):
    folder = path.expanduser("~")
    logFile = path.join(folder , "AppData/Local/GoTo/GoToShutdown/error.txt")
    logging.basicConfig(filename=logFile , level=logging.ERROR)
    logging.error(str(error)+" "+str(datetime.datetime.now()))

def alert(head , message , icon=None):
    try:
        notification.notify(
            title = head,
            message = message,
            app_icon = icon,
            timeout = 10
        )
    except Exception as e:
        log(e)
        return False

def check_txt_len(txt , target_len , added_num):
    if len(txt) == target_len:
        return txt
    else:
        return f"{added_num}{txt}"

def save_to_db(db , cr , title , hours , minute , period):
    try:    
        cr.execute("INSERT INTO times values(? , ? , ? , ?)", (title , hours , minute , period))
        db.commit()
        return True
    except Exception as e:
        log(e)
        return False

def json_dump(result , file_name):
    with open(file_name , "w") as file:
        json.dump(result , file , indent=4)
        file.close()

def json_load(file_name):
    with open(file_name , "r") as file:
        res = json.load(file)
        file.close()
    return res

def db_get(cr,query,type) -> list:
    """
    cr : enter the cursor of your database
    query : enter the query to be executed
    type : do you want your data to be fetched all or fetchone (fetchall or fetchone)
    """
    try:
        if type == "fetchall":
            data = cr.execute(query).fetchall()
        elif type == "fetchone":
            data = cr.execute(query).fetchone()
        return data
    except Exception as e:
        log(e)
        return False
        

def db_del(db , cr , query , target):
    """
    db : insert the database variable usually named db
    cr : insert the cursor of the database
    query: insert the deletion process query
    target : insert the target that you want to delete to check if there any errors and prevent sql injection
    """
    try:
        cr.execute(query,(target,))
        db.commit()
        qr = "SELECT * from times"
        data = db_get(cr,qr,"fetchall")
        for tu in data:
            for item in tu:
                if item == target:
                    return False
        return data
    except Exception as e:
        log(e)
        return False
        

def db_edit(db , cr , query , tu , title):
    """
    db : insert the database variable
    cr : insert the cursor of the database
    query : insert the editing process query
    tu : insert the values of the editing process to prevent sql injection
    title : insert the old title of the record to ensure that the value has been edited
    """
    try:
        cr.execute(query , tu)
        db.commit()
        data = db_get("*" , "times" , "fetchall" , cr)
        for tu in data:
            for item in tu:
                if item == title:
                    return False
        return True
    except Exception as e:
        log(e)
        return False
        

def addToReg():
    # add app to registry for autostart called automatic.py
    import winreg
    import os
    fileDir = os.path.dirname(os.path.abspath(__file__))
    fullname = os.path.join(fileDir, "autoshut.exe")
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, "autoshut", 0, winreg.REG_SZ, fullname)
    winreg.CloseKey(key)


def removeFromReg():
    # remove app from registry for autostart called automatic.exe
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteValue(key, "autoshut")
    winreg.CloseKey(key)
