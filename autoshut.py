import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import datetime
import sqlite3,asset,filteringSystem
import os



class MainWindow():
    def __init__(self,root) -> None:
        self.main_window = root # creating the variable of the main window provided when creating an object
        mainDir = os.path.dirname(os.path.abspath(__file__)) # the location of the current folder of the application
        self.db = sqlite3.connect(os.path.join(mainDir,"times.db")) # connecting to the database in the current folder
        self.cr = self.db.cursor() # creating the cursor
        dirname = os.path.dirname(__file__) # getting the name of the folder
        self.cr.execute("CREATE TABLE IF NOT EXISTS times(title text,hour text,min text,period text)") # creating the times table of not exists
        qr = "SELECT * FROM times" # to find any time saved in the database
        times = [time[0] for time in asset.db_get(self.cr , qr , "fetchall")] # creating a list with all the avaliable times

        if len(times) != 0: # if there is any saved time start the shutdown process automatically
            self.shutdown()
        
        json_check = os.path.exists(os.path.join(dirname,"config.json")) # checking if the json file exists
        if json_check == False: # if it doesn't exist create a file
            asset.create_json()
        
        check = asset.json_load("config.json") # loading the file
        
        if check["error file"] == False: # if the log file doesn't exist create a one
            asset.create_logging_folder()
            check["error file"] = True # make it true
            asset.json_dump(check , "config.json")
        

    def shutdown(self):
        today = datetime.datetime.today() # getting the current day date
        qr = "SELECT * FROM times" # a query for extracting all the existing time in the database
        times = [time[0] for time in asset.db_get(self.cr , qr , "fetchall")] # creating a list to deal with
        current = datetime.datetime.now().strftime("%I:%M %p") # formating the current time formart with a more readable format
        nearest_time = filteringSystem.ftime(times,current) # applying an algorithm to return the nearest time to our current time
        nearest_time = today.replace(hour=nearest_time.hour,minute=nearest_time.minute,second=0,microsecond=0) # replacing the time of today to the nearest time gotten from the algorithm
        print(nearest_time) # checking the value
        current = datetime.datetime.strptime(current,"%I:%M %p") 
        current = today.replace(hour=current.hour,minute=current.minute,second=datetime.datetime.now().second,microsecond=0) # formatting the current time to compare with the future time
        if(nearest_time < current): # if the current time is ahead of the next time then increase a day for the future date (like if the time is 3 am and you are at 11 pm you should a day difference to get the correct difference)
            nearest_time += datetime.timedelta(days=1)
        sec = (nearest_time-current).total_seconds() # getting the amount of seconds
        print(sec)
        os.system(f"shutdown /s /t {int(sec)}") # shutdown the pc given the amount of seconds

    def abort(self): # aborting the shutdown
        os.system(f"shutdown -a")
        
        

    def save(self):
        hour = self.hours.get()
        minu = self.minutes.get()
        per = self.period.get()
        if(len(minu) < 2):
            minu = '0'+minu
        if(len(hour) < 2):
            hour = '0'+hour
        print(hour , minu, type(per))
        if hour == '' or minu == '' or per == '':
            asset.alert("Missing Values" , "There is a missing input/s please check all data entries and try again","1827301.ico")
        else:
            now = datetime.datetime.now().strftime("%I:%M %p")
            save = asset.save_to_db(self.db,self.cr,hour+':'+minu+' '+per,hour,minu,per)
            if(save):
                pass
            else:
                asset.alert("Error","There was an error saving the time please try again")

    def delete(self):
        td = self._times.get()
        #DELETE FROM {table} where {wanted_row} = '{dname}'
        qr = f"DELETE FROM times where title = ?"
        del_res = asset.db_del(self.db,self.cr,qr,td)
        if(del_res != False):
            if(len(del_res) > 0):
                self._times['values'] = [time[0] for time in del_res]
                self._times.set('')
            else:
                self.del_btn['state'] = 'disabled'
                self._times.set('') 
        else:
            asset.alert("Error","There was an error deleting the time please try again")
    
    def show_times(self):
        times_window = tk.Toplevel(self.main_window)
        times_window.title("Times")
        times_window.geometry("200x200")
        query = "SELECT * FROM times"
        times_list = asset.db_get(self.cr,query,"fetchall")
        self._times = ttk.Combobox(times_window,values=[time[0] for time in times_list])
        self._times.pack()
        self.del_btn = ttk.Button(times_window,text="Delete",command=self.delete)
        self.del_btn.pack()
        data = asset.db_get(self.cr,query,"fetchall")
        if len(data) == 0:
            self.del_btn['state'] = "disabled"

    def autostart(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        auto = asset.json_load(os.path.join(dirname,"config.json"))
        auto['autostart'] = True
        asset.addToReg()
        self.auto_btn.configure(text="Disable Autostart",command=self.disable_autostart)
        asset.json_dump(auto,os.path.join(dirname,"config.json"))

    def disable_autostart(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        auto = asset.json_load(os.path.join(dirname,"config.json"))
        auto['autostart'] = False
        asset.removeFromReg()
        self.auto_btn.configure(text="Enable Autostart",command=self.autostart)
        asset.json_dump(auto,os.path.join(dirname,"config.json"))

    def construct_window(self,title:str,size:str,resizeable:bool):
        self.main_window.geometry(size)
        self.main_window.title(title)
        self.main_window.resizable(width=resizeable,height=resizeable)

        dirname = os.path.dirname(os.path.abspath(__file__))
        auto = asset.json_load(os.path.join(dirname,"config.json"))

        title_lbl = tk.Label(self.main_window,text="AutoShut",font=("BroadWay",15,"bold"))
        title_lbl.place(rely=0.01,relx=0.35)

        self.hours = tk.Spinbox(self.main_window,from_=1,to=12)
        self.hours.place(rely=0.1,relx=0.35)
        hours_lbl = tk.Label(self.main_window,text="Hours",font=("Helvetica",8,"bold"))
        hours_lbl.place(rely=0.1,relx=0.7)

        self.minutes = tk.Spinbox(self.main_window,from_=00,to=59)
        self.minutes.place(rely=0.2,relx=0.35)
        minutes_lbl =tk.Label(self.main_window,text="Minutes",font=("Helvetica",8,"bold"))
        minutes_lbl.place(rely=0.2,relx=0.7)

        self.period = ttk.Combobox(self.main_window,values=['PM','AM'])
        self.period.place(rely=0.3,relx=0.34)

        times_btn = ttk.Button(self.main_window,text="Times",command=self.show_times)
        times_btn.place(rely=0.001,relx=0.005)

        self.auto_btn = ttk.Button(self.main_window,text="Enable AutoStart",command=self.autostart)
        self.auto_btn.place(rely=0.001,relx=0.75)
        if(auto['autostart'] == True):
            self.auto_btn.configure(text="Disable Autostart",command=self.disable_autostart)

        save_btn = ttk.Button(self.main_window,text="Save",command=self.save)
        save_btn.place(rely=0.4,relx=0.41)

        shut_btn = ttk.Button(self.main_window,text="Shutdown",command=self.shutdown)
        shut_btn.place(rely=0.5,relx=0.41,relwidth=0.2,relheight=0.1)

        abort_btn = ttk.Button(self.main_window,text="Abort",command=self.abort)
        abort_btn.place(rely=0.6,relx=0.41,relwidth=0.2,relheight=0.1)
        
        
    

if __name__ == '__main__':
    master = tk.Tk()
    window = MainWindow(master)
    window.construct_window("AutoShut","400x500",False)
    master.mainloop()