import numpy as np
import matplotlib.pyplot as pl
from language_processing import *
from extract_data import *
from loader import *
import re

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

def get_doc_dates_and_keywords(patient_data, keywords, dates, counts, count_elements = True, by_doc_type = False):
    if counts == None:
        counts = dict()
    if dates == None:
        dates = dict()
    procedure_date = get_operation_date(patient_data)
    if procedure_date == None:
        return (docs_before, docs_after)
    else: 
        print procedure_date, "####", patient_data.keys()
        for doc_type in patient_data:
            date_key = get_date_key(doc_type)
            print doc_type, date_key
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
                            difftime = date - procedure_date
                            if doc_type in dates:
                                dates[doc_type] += [difftime]*multiplier
                            else:
                                dates[doc_type] = [difftime]*multiplier
                            
                            if is_note_doc(doc_type):
                                note = doc['free_text'].lower()
                                for key in keywords:
                                    pattern = re.compile(key)
                                    if by_doc_type:
                                        if not doc_type in counts:
                                            count[doc_type] = dict()
                                        if key in counts[doc_type]:
                                            counts[doc_type][key] += [difftime] *len(re.findall(pattern, note))
                                        else:
                                            counts[doc_type][key] = [difftime] * len(re.findall(pattern, note))
                                    else:
                                        if key in counts:
                                            counts[key] += [difftime] * len(re.findall(pattern, note))
                                        else:
                                            counts[key] = [difftime] * len(re.findall(pattern, note))
                                            
            return (dates, counts)

def plot_num_docs(patient_range = range(90)):
    rel_dates = dict()
    keyword_counts = dict()
    keywords = ['ef\w+(.+)%', 'ejection fraction:\w*(.+)%', 'ef of (.+)%','ejection fraction of (.+)%', 'ef is (.+)%', 'ef:\w*(.+)%','ejection fraction is (.+)%', 'ef:\w*(.+)%']
    overall_counts = dict()
    for i in patient_range:
        data = get_data([i])[0]
        #rel_dates, keyword_counts = get_doc_dates_and_keywords(data, keywords, rel_dates, keyword_counts)
        rel_dates = get_doc_rel_dates(data, rel_dates)
        #keyword_counts = get_doc_keywords(data, keywords, keyword_counts, True)
        ef_occurances = get_ef_values(data, car_only = True)
        if False and len(ef_occurances) > 2: #REMOVE FALSE TO SEE PLOTS
            dates, efs = zip(*ef_occurances)
            pl.figure()
            pl.scatter(dates, efs)
            pl.show()
        #for doc in keyword_counts:
        #    s = 0
        #    for key in keyword_counts[doc]:
        #        s += len(keyword_counts[doc][key])
        #    
        #    if not doc in overall_counts:
        #        overall_counts[doc] = [s]
        #    else:
        #        overall_counts[doc] += [s]
    
   # print overall_counts['Car']
   # pl.figure()
   # pl.hist(overall_counts['Car'])
   # pl.show()

    #for keyword in keyword_counts:
    #    print keyword, ": ", str(sum(keyword_counts[keyword]))
    #for doc in keyword_counts:
    #    print doc
    #    for keyword in keyword_counts[doc]:
    #        print "\t", keyword, ": ", str(sum(keyword_counts[doc][keyword]))
    note_deltas = []
    struct_deltas = []
    for doc_type in rel_dates:
        if is_note_doc(doc_type):
            note_deltas += [x.days for x in rel_dates[doc_type]]
        else:
            struct_deltas += [x.days for x in rel_dates[doc_type]]
    for word in keyword_counts:
        keyword_counts[word] = [x.days for x in rel_dates[doc_type]]
    
    bins = 100    
    print
    print "Notes: ", len(note_deltas)
    print "Structs: ", len(struct_deltas)
    pl.figure()
    h = pl.hist([note_deltas, struct_deltas], bins,stacked = True, color = ['blue', 'red'], label = ['Number of sentences in\nunstructured notes', 'Number of structured data fields'])
    pl.legend(loc = 2)
    pl.title("Frequency of Occurances of New Data in Cohort")
    pl.xlabel("Days Since Implant Procedure")
    pl.ylabel("Number of Data Elements")
    pl.show()


    for word in keyword_counts:
        pl.figure()
        pl.hist(keyword_counts[word], bins, color = ['blue'])
        pl.title("Occurances of " + word + " in corpus at time from procedure")
        pl.show()

    
