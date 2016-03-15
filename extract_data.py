from language_processing import parse_m_d_y, parse_m_y, parse_date, format_date, split_sentences
import re
import datetime
from datetime import timedelta

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


def get_doc_rel_dates(patient_data, dates = None, count_elements = True):
    if dates == None:
        dates = dict()
    procedure_date = get_operation_date(patient_data)
    if procedure_date == None:
        return dates 
    else: 
        for doc_type in patient_data:
            date_key = get_date_key(doc_type)
            if date_key != None:
                docs = patient_data[doc_type]
                if type(docs) != type(list()):
                    docs = [docs]
                for doc in docs:
                    if doc != None:
                        date = parse_date(doc[date_key])
                        if date != None:
                            multiplier = 1
                            if count_elements:
                                if is_note_doc(doc_type):
                                    multiplier = len(split_sentences(doc['free_text']))
                                else:
                                    multiplier = len(doc.keys())
                            if doc_type in dates:
                                dates[doc_type] += [date - procedure_date]*multiplier
                            else:
                                dates[doc_type] = [date - procedure_date]*multiplier
    return dates


'''
description
    returns a list of (date, EF_value) tuples generated from the notes of a patient from get_data([i])
inputs
    patient_data: dictionary of docs as returned by get_data([i])[0]
    car_only: boolean flag that only looks at Car notes
output
    list of (date, EF_value) tuples that can be post-processed into counts, a plot of estimated EF, or estimate for EF prefore and after delta for procedure
    the date is 0-centered around procedure date
''' 
def get_ef_values(patient_data, car_only = True): 
    keywords = ['ef[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%', 'ejection fraction[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%']
    keywords = ['(?:ef|ejection fraction)\s*(?:of|is)?[:\s]*([0-9]*\.?[0-9]*)\s*%']
    results = []
    procedure_date = get_operation_date(patient_data)
    if procedure_date == None: #throw out patient if no procedure date
        return results
    else: 
        for doc_type in patient_data: #loop over each doc type, eg Enc, Lno
            if is_note_doc(doc_type) and (not car_only or doc_type == 'Car'): #only look at note docs, eg Car, Lno
                date_key = get_date_key(doc_type)
                if date_key != None: #only look at notes with a date key provided (should be all of them)
                    docs = patient_data[doc_type]
                    if type(docs) != type(list()): #just in case the value is not a list, make it one so we can iterate over it
                        docs = [docs]
                    for doc in docs: #for each document of that type for a given patient
                        if doc != None: #assuming the list is not empty
                            date = parse_date(doc[date_key]) #this stores the date of the note
                            if date != None: #if there is a date value
                                note = doc['free_text'].lower() #get the note raw_text
                                delta_days = (date - procedure_date).days
                                ##### MODIFY THIS PART ###### -- Has been modified by mtraub
                                for key in keywords: #for each keyword, search over the document and get matched MODIFY THIS
                                    pattern = re.compile(key)
                                    results += [ (delta_days, float(x)) for x in re.findall(pattern, note) if len(x) > 0 and x != "."]
    return results

'''
ADDED BY JOSH TO VALIDATE
'''
def get_ef_value_notes(patient_data, car_only = True):

    keywords = ['(?:ef|ejection fraction)\s*(?:of|is)?[:\s]*([0-9]*\.?[0-9]*)\s*%']
    keywords = ['ef[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%', 'ejection fraction[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%']
    results = []
    procedure_date = get_operation_date(patient_data)
    if procedure_date == None: #throw out patient if no procedure date
        return results
    else: 
        for doc_type in patient_data: #loop over each doc type, eg Enc, Lno
            if is_note_doc(doc_type) and (not car_only or doc_type == 'Car'): #only look at note docs, eg Car, Lno
                date_key = get_date_key(doc_type)
                if date_key != None: #only look at notes with a date key provided (should be all of them)
                    docs = patient_data[doc_type]
                    if type(docs) != type(list()): #just in case the value is not a list, make it one so we can iterate over it
                        docs = [docs]
                    for doc in docs: #for each document of that type for a given patient
                        if doc != None: #assuming the list is not empty
                            date = parse_date(doc[date_key]) #this stores the date of the note
                            if date != None: #if there is a date value
                                note = doc['free_text'].lower() #get the note raw_text
                                delta_days = (date - procedure_date).days
                                ##### MODIFY THIS PART ###### -- Has been modified by mtraub
                                for key in keywords: #for each keyword, search over the document and get matched MODIFY THIS
                                    pattern = re.compile(key)
                                    results += [ (delta_days, float(x), note) for x in re.findall(pattern, note) if len(x) > 0 and x != "."]
    return results



def get_doc_keywords(patient_data, keywords, counts = None, by_doc_type = False):
    if counts == None:
        counts = dict()
    for doc_type in patient_data:
        if is_note_doc(doc_type):
            docs = patient_data[doc_type]
            for doc in docs:        
                note = doc['free_text'].lower()
                for key in keywords:
                    pattern = re.compile(key)
                    if by_doc_type:
                        if not doc_type in counts:
                            counts[doc_type] = dict()
                        if key in counts[doc_type]:
                            counts[doc_type][key] += [len(re.findall(pattern, note))]
                        else:
                            counts[doc_type][key] = [len(re.findall(pattern, note))]
                    else:
                        if key in counts:
                            counts[key] += [len(re.findall(pattern, note))]
                        else:
                            counts[key] = [len(re.findall(pattern, note))]
                    
    return counts

def get_doc_rel_dates(patient_data, dates = None, count_elements = True):
    if dates == None:
        dates = dict()
    procedure_date = get_operation_date(patient_data)
    if procedure_date == None:
        return dates 
    else: 
        for doc_type in patient_data:
            date_key = get_date_key(doc_type)
            if date_key != None:
                docs = patient_data[doc_type]
                if type(docs) != type(list()):
                    docs = [docs]
                for doc in docs:
                    if doc != None:
                        date = parse_date(doc[date_key])
                        if date != None:
                            multiplier = 1
                            if count_elements:
                                if is_note_doc(doc_type):
                                    multiplier = len(split_sentences(doc['free_text']))
                                else:
                                    multiplier = len(doc.keys())
                            if doc_type in dates:
                                dates[doc_type] += [date - procedure_date]*multiplier
                            else:
                                dates[doc_type] = [date - procedure_date]*multiplier
    return dates

def is_note_doc(doc_type):
    return doc_type.upper() in ["LNO", "CAR", "RAD", "PAT", "OPN", "DIS", "MIC", "PUL"]

def get_date_key(doc_type):
    keys = {u'Enc': u'Discharge_Date', u'Pat': u'date', u'Mic': u'date', u'Pul': u'date', u'Med': u'Medication_Date', u'Lab': u'Seq_Date_Time', u'Phy': u'Date', u'Opn': u'date', u'Lme': u'LMR_Medication_Date_Time', u'Rdt': u'Date', u'Lvs': u'LMR_Vital_Date_Time', u'Trn': u'Transaction_Date_Time', u'Car': u'date', u'Lhm': u'LMR_Health_Maintenance_Date_Time', u'Dia': u'Date', u'Lpr': u'LMR_Problem_Date', u'Dis': u'date', u'Rad': u'date', u'Prc': u'Date', u'Lno': u'date'}
    if doc_type in keys:
        return keys[doc_type]
    else:
        return None

'''
description
    parses the notes header
input
    header_string: the first line of the notes document
output
    dictionary of values with keys ['date', 'doctor', 'hospital']
'''
def parse_note_header(head_string, doc_type):
    if not is_note_doc(doc_type):
        return dict()
    result = {'Date' : None, 'Doctor' : None, 'Hospital' : None, 'Procedure' : None}
    head_split = head_string.split("|")
    #print head_split
    result['Hospital'] = head_split[1]
    doc_type = doc_type.upper()
    if doc_type == "LNO":    
        result['Date'] = head_split[3].split()[0]
        result['Doctor'] = head_split[6]
        result['Procedure'] = head_split[10]
    elif doc_type in [ "DIS" , "CAR",  "RAD" , "PAT" , "OPN" ]:
        result['Date'] = head_split[5].split()[0]
        result['Procedure'] = head_split[6]
    elif doc_type in [  "MIC" , "PUL" ]:
        result['Date'] = head_split[4].split()[0]
        result['Procedure'] = head_split[5]
    
    if result['Date'] != None:
        result['Date'] = format_date(result['Date'])    
    return result
