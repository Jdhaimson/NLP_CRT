import numpy as np
import matplotlib.pyplot as pl
from language_processing import *
from extract_data import *
from loader import get_data
from extract_data import get_doc_rel_dates, get_ef_values, get_doc_keywords
import re

def plot_num_docs(patient_range = range(90)):
    rel_dates = dict()
    keyword_counts = dict()
    keywords = ['ef\w+(.+)%', 'ejection fraction:\w*(.+)%', 'ef of (.+)%','ejection fraction of (.+)%', 'ef is (.+)%', 'ef:\w*(.+)%','ejection fraction is (.+)%', 'ef:\w*(.+)%']
    overall_counts = dict()
    for i in patient_range:
        if i % 25 == 0:
            print i
        data = get_data([i])[0]
        rel_dates = get_doc_rel_dates(data, rel_dates, True)
        #keyword_counts = get_doc_keywords(data, keywords, keyword_counts, True)
        #ef_occurances = get_ef_values(data, car_only = True)
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
    h = pl.hist([note_deltas, struct_deltas], bins,stacked = True, color = ['blue', 'red'], label = ['Number of sentences in\nunstructured notes', 'Number of structured entries'])
    pl.legend(loc = 2)
    pl.title("Frequency of Occurances of New Data in Patient")
    pl.xlabel("Days Since Implant Procedure")
    pl.ylabel("Number of Pieces of Information")
    pl.show()


    for word in keyword_counts:
        pl.figure()
        pl.hist(keyword_counts[word], bins, color = ['blue'])
        pl.title("Occurances of " + word + " in corpus at time from procedure")
        pl.show()

    
