from loader import * 
from language_processing import *
from extract_data import *
from build_graphs import *

if raw_input("Do you want to generate plots? (y/n) ").lower() == 'y':
    lower_range = int(raw_input("Lower bound on range (0-912): "))
    upper_range = int(raw_input("Upper bound on range (1-913): "))
    plot_num_docs(range(lower_range, upper_range))

if raw_input("Do you want to test the document date fields? (y/n) ").lower() == 'y':
    doc_dates = dict()
    for i in range(50):
        data = get_data([i])[0]
        for doc_type in data:
            if data[doc_type] != None:
                doc = data[doc_type]
                if type(doc) != type(list()):
                    doc = [doc]
                if len(doc) > 0:
                    doc = doc[0]
                    for label in doc:
                        if "date" in label.lower():
                            if doc_type in doc_dates:
                                doc_dates[doc_type].add(label)
                            else:
                                doc_dates[doc_type] = set([label])
    print doc_dates

if raw_input("Do you want to test operation date extractor? (y/n) ").lower() == 'y':    
    #Test the procedure date extractor
    for i in range(1000):
        data = get_data([i])[0]
        print get_operation_date(data)

print "==================================================="

#Test the file extractor
if raw_input("Do you want to test parse_note_header? (y/n) ").lower() == 'y':
    for i in range(50):
        data = get_data([i])[0]
        clean_data(data)
        for tag in data:
            data_tag = data[tag]
            for doc in data_tag:
                parsed = parse_note_header(doc, tag)
                if len(parsed) > 0:
                    print tag, parsed

#Explore a patient's data
again = True
maxkey = 900
while again:    
    num = -1
    while not unicode(num).isnumeric() or int(num) < 0 or int(num) >= maxkey:
        num = raw_input("Select a patient number from 0 - " + str(maxkey) + ": ")
    num = int(num)
    patient = dict(get_data([num])[0])
    clean_data(patient)

    explore(patient)
    inp = raw_input("Look at another patient? (y/n): ")
    again = inp.lower() == "y" or (unicode(inp).isnumeric())


s = "Hello person. I weigh 15.6kg. How about you?I think you are 20.Correct?"
print split_sentences(s)

#See the entire bag of words for the 'Lno' field across all patients 
'''
if raw_input("Enter 'y' to see bag of words test:") == "y":
    print
    x = raw_input("This is about to output the entire bag of words for all patients\nin their Lno file. Press enter to continue")
    print 
    tag = u'Lno'
    bag = bag_of_words(data[data.keys()[0]][tag])
    for i in range(1, len(data.keys())):
        person = data[data.keys()[i]]
        if tag in person:
            bag = bag_of_words(person[tag], bag)
           
    tuple_bag = [(str(k), bag[k]) for k in bag]
    print sorted(tuple_bag, key = lambda k: k[1], reverse = True)

'''
