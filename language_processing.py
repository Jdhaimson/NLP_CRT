from extract_data import *

#----------------------------------------------------------
# Functions for parsing the header of a note file and modifying
# the JSON to incorporate these structured fields
#----------------------------------------------------------

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

'''
description
    given data, which can be text, a JSON, or a list of these, and the type of document
    we return a new JSON with the sturctured fields pulled out from parse_note_header
input
    data: a string, JSON, or list of these
    doc_type: the tag of the type of document, e.g. Lno, Enc
output:
    --if a string given and string represents a note, then a JSON with the note and the 
      structured fields extracted
    --if string but is not a note, then just the string
    --if a JSON, then return the same
    --if a list, then a list of the same size with each element modified as above
'''
def add_structured_fields(data, doc_type):
    pass

#----------------------------------------------------------
# Functions for extracting sentences from text
#----------------------------------------------------------


'''
description
    given an index in a string i, extracts the sentence [a, b] where b >= i
    this means if s[i] = '.', then this will return the preceeding sentence
input
    s: a string
    i: the index of the string that should be contained in the output sentence
    index: if true, then the indicies [a, b) that define the sentence are returned
        otherwise, the string s[a:b] is returned (default FALSE)
output
    if index = TRUE
        a tuple (a, b)
    else
        a string s[a, b)
'''
def get_sentence(s, i, index = False):
    #A new line must end a sentence and no ne gives a fuck about '\r'
    s = s.replace("\r", "")
    s = s.replace("\n", ". ")#TODO: more careful way of achieving this effect

    a = i-1
    #find the end of the previous sentence
    while a > 0 and not is_sentence_end(s, a-1):
        a -= 1
    b = i
    #find end of sentence
    while b < len(s) and not is_sentence_end(s, b):
        b += 1

    #return tuple or string based on index variable
    if index:
        return (a, b+1)
    else:
        return s[a : b+1]

'''
description
    uses get_sentence to tokenize string into sentences
input
    s: string
output
    a list of sentences
'''
def split_sentences(s):
    s = s.replace("\r","").replace("\n", ". ")
    i = 0
    result = []
    while i < len(s):
        a, i_new = get_sentence(s, i, True)
        result += [s[i:i_new].strip(" ")]
        i = i_new
    return result



'''
description
    helper function to help identify if '.' in a string indicates if a sentence ends
input
    s: a string
    i: the index of the '.'
output
    boolean of if that '.' indicates an end of a sentence
'''
def is_sentence_end(s, i):
    if i == 0: #if period starts string, not end of sentence
        return False
    elif i >= len(s)-1: #if period ends string, must be end of sentence
        return True
    elif unicode(s[i]) in [u'!',u'?']: #these are unambiguous
        return True
    elif unicode(s[i]) != u'.': #if its not a period it can't end a sentence
        return False
    else: #this is the case that it is a period 
        before = unicode(s[i-1])
        after = unicode(s[i+1])
        if not before.isnumeric(): #e.g. "...and he stopped. 5 is a nice number"
            return True
        elif after.isnumeric(): #e.g. "I have 5.2 liters"
            return False
        else: #e.g. "I have work until 5.I need a friend"
            return True
    #TODO: include cases for Mr. , Mrs. or any arbitary list of abreviations


#----------------------------------------------------------
# Functions for generating a bag of words and combining these
#----------------------------------------------------------

'''
decription  
    pulls out a dictionary of word counts from a document
inputs 
    doc: string
    vocabulary: bag of words to build on (default is None)
outputs
    dictionary of words with counts
details
    uses clean_word method to remove punctation and get rid of numeric tokens
    all words converted to lower-case
'''
def bag_of_words(doc, vocabulary = None):
    bag = dict()
    if vocabulary != None:
        bag = vocabulary
    #replace all punctuation that will never be in a word
    #with spaces (e.g. \r, \n, ',', =>)
    doc = doc.lower()
    doc = doc.expandtabs(1)
    doc = doc.replace("\r", " ").replace("\n", " ").replace("->", " ")
    doc = doc.replace(",", " ").replace("=>", " ")
    #split by spaces
    words = doc.split(" ")
    for word in words: #for each word clean it and insert into bag
        word = clean_word(word)        
        if word in bag:
            bag[word] += 1
        else:
            bag[word] = 1
    bag.pop("") #remove the "" word
    return bag

def clean_word(word):
    charList = list(word)
    #if any numbers in the word, remove the word (by returning empty string)
    hasNumeric = any([unicode(l).isnumeric() for l in charList])
    if hasNumeric:
        word = u''
    else:
        #if any of these symbols in the word, then it is not a word
        hasSym = any([l in [u'|', u'/',u'_',u'*'] for l in charList])
        if hasSym:
            word = u''
        else:
            last = ""
            #remove these chars from outside of word until none present
            while word != last:
                last = word
                word = word.strip(".").strip(",").strip(":").strip("-").strip("+").strip("<")
                word = word.strip("?").strip(";").strip("(").strip(")")
                word = word.strip("\"").strip(">").strip("[").strip("]")
    return unicode(word)

'''
Given two dictionaries of word counts, makes one dictionary of combined word counts
'''
def combine_bags(dict1, dict2):
    result = dict()
    keys1 = dict1.keys()
    for k in keys1:
        if k in dict2:
            result[k] = dict1.pop(k) + dict2.pop(k)
        else:
            result[k] = dict1.pop(k)
    keys2 = dict2.keys()
    for k in keys2:
        if k in dict1:
            result[k] = dict1.pop(k) + dict2.pop(k)
        else:
            result[k] = dict2.pop(k)
    return result


