import re
import datetime
from datetime import timedelta


#----------------------------------------------------------
# Functions for parsing the header of a note file and modifying
# the JSON to incorporate these structured fields
#----------------------------------------------------------

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


