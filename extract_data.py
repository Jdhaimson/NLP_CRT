import loader
import re
import datetime
from datetime import timedelta

#eventually this should add the field "Operation Date" to procedure that contains the parsed date
def get_operation_date(patient_data):
    status = patient_data['Procedure']['Implant Status']
    match = parse_m_d_y(status)
    if not match:
       match = parse_m_y(status)
    oneMo = parse_m_d_y(patient_data['Procedure']['1 Mo. Appt'])
    threeMo = parse_m_d_y(patient_data['Procedure']['3 Mo. Appt'])
    
    #checks if match makes sentence given the 1 month and 3 month checkups
    if match:
        if oneMo and threeMo:    
            lower_range = max(threeMo - timedelta(days = 30*24), oneMo - timedelta(days = 30*6))
            upper_range = min(threeMo - timedelta(days = 30*2), oneMo) 
        elif not oneMo and threeMo:
            lower_range = threeMo - timedelta(days = 30*24)
            upper_range = threeMo - timedelta(days = 30*2) 
        elif oneMo and not threeMo:
            lower_range = oneMo - timedelta(days = 30*6)
            upper_range = oneMo
        else:
            lower_range = datetime.date(datetime.MINYEAR, 1, 1)
            upper_range = datetime.date(datetime.MAXYEAR, 1, 1)
        if lower_range > match or upper_range < match:
            match = None

    #if no good date found, subtrack from one month and three month checkups
    if not match:
        if oneMo:
            match = oneMo - timedelta(days = 30)
        elif threeMo:
            match = threeMo - timedelta(days = 90)
        else:
            return None
    
    return match

def parse_m_d_y(s):
    # I (Josh) added this to catch a date that had a typo in it
    s = s.replace(".", '')
    re_m_d_y = r"([0-9]{1,2})[/-]([0-9]{1,2})[/-]([0-9]{4})|([0-9]{1,2})[/-]([0-9]{1,2})[/-]([0-9]{2})"
    match = re.search(re_m_d_y, s)   
    if match:
        groups = list(match.groups())
        if groups[0] == None:
            groups = groups[3:]
            if int(groups[2]) - 17 >= 0:
                groups[2] = '19' + groups[2]
            else:
                groups[2] = '20' + groups[2]
        else:
            groups = groups[:3]
        return datetime.date(int(groups[2]),int(groups[0]),int(groups[1]))
    else:
        return None

def parse_m_y(s):
    re_m_y = "([0-9]{1,2})/([0-9]{4})|([0-9]{1,2})/([0-9]{2})"
    match = re.search(re_m_y, s)   
    if match:
        groups = list(match.groups())
        if groups[0] == None:
            groups = groups[2:]
            if int(groups[1]) - 17 >= 0:
                groups[1] = str(19) + groups[1]
            else:
                groups[1] = str(20) + groups[1]
        else:
            groups = groups[:2]
       
        return datetime.date(int(groups[1]),int(groups[0]), 1)
    else:
        return None

def parse_date(s):
    date = parse_m_d_y(s)
    if not date:
        date = parse_m_y(s)
    if not date:
        return None
    return date

def format_date(s):
    if type(s) in [type(""), type(u'')]:
        date = parse_date(s)
    else:
        date = s
    return date.strftime("%m/%d/%Y 00:00")

