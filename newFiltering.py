import datetime

def ftime(timeList:str , ntime:str):
    ntime = datetime.datetime.strptime(ntime,"%I:%M %p")
    pm_list = [datetime.datetime.strptime(time,"%I:%M %p") for time in timeList if time.lower().endswith("pm") == True]
    am_list = [datetime.datetime.strptime(time,"%I:%M %p") + datetime.timedelta(1) for time in timeList if time.lower().endswith("am") == True]
    nearst = None
    if len(pm_list) != 0:
        nearst = pm_list[0]
        for time in pm_list:
            time = datetime.datetime.strptime(time,"%I:%M %p")
            if time == nearst:
                continue
            if time > ntime and time < nearst:
                nearst = time
    else:
        nearst = am_list[0]
        for time in am_list:
            time = datetime.datetime.strptime(time,"%I:%M %p")
            if time == nearst:
                continue
            if time > ntime and time < nearst:
                nearst = time

    return nearst





    